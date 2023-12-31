import os
import openai
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

# ask chat gpt
def generate_profile_summary(df, input_name: str, out_words: int, gpt_model: str):

    # input
    prompt = generate_prompt_from_data(df, input_name, out_words)

    response = completion_with_backoff(
        model = gpt_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes staff profile summaries."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']
