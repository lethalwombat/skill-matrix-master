import os
import openai
from helpers_data import df_filter_multiple
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff


# get the gpt api key and authenticate
API_KEY = os.getenv('GPT_API_KEY')
openai.api_key = API_KEY

# define the exponential back-off request
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return openai.ChatCompletion.create(**kwargs)

# generate the prompt from data
def generate_prompt_from_data(df, input_name: str, out_words: int):
    skill_list = (
        df
        .query('relevance in ["Focus", "Red hot"]')
        [['consultant_name', 'technology', 'skill_rating']]
        .query('consultant_name == @input_name')
        .query('skill_rating >= 3')
        ['technology'].str.strip()
        .to_list()
    )
    return \
        '''
        {} is proficient in the skills separated by comma: {} .{} works as consulant in the data and
         analytics industry. 
        Provide a profile summary for {} in
        {} words or less, use Australian English and avoid using the names of the provided skills in your response.
        '''.format(
        input_name, ','.join(skill_list), input_name, input_name, out_words, input_name
    ).replace('\n', ' ').strip()

# generate the prompt from data for the capability
def generate_prompt_from_data_capability(df, input_name: list, out_words: int):
    df_pool = (
        df
        .pipe(df_filter_multiple, input_name, 'persona_stream')
        [['technology', 'relevance', 'consultant_name', 'skill_rating']]
        .query('relevance in ["Focus", "Red hot"]')
        .query('skill_rating >= 4')
    )
    # the pool is too small for a prompt
    if df_pool.shape[0] < 10:
        return ''
    
    table_skilled = (
        df_pool
        .groupby('technology')
        .count()
        .reset_index()
        [['technology', 'skill_rating']]
        .to_string(index=False, header=False)
    )

    return \
        '''
        Below is the list of technology names followed by the number of 
        consultants skilled in the technology for the "{}" capability. Provide an overview of the technology areas
        where there is  enough skills and identify current and potential skill gaps.
        {}. Recommend additional emerging technologies 
        to upskill in in the "{}" capability.
        Provide the result in {} words or less. 
        '''.format(','.join(input_name), table_skilled, ','.join(input_name), out_words)

# ask chat gpt
def generate_profile_summary(df, input_name, out_words: int, gpt_model: str):
    
    prompt = df
    # convert input to string prompt
    if not isinstance(df, str):
        prompt = generate_prompt_from_data(df, input_name, out_words)

    response = completion_with_backoff(
        model = gpt_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes staff profile summaries"},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']
