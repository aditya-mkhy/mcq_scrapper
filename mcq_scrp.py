import requests
from bs4 import BeautifulSoup
import re
import json


class Scrapper:
    def __init__(self):
        self.data = []

    def get_ans(self, soup: BeautifulSoup):
        ans_script = None # script with ans

        scripts = soup.find_all('script')
        for script in scripts:
            script = str(script) # conver into string...

            if "answer" in script :
                ans_script = script
                break

        if not ans_script:
            return {}

        answers = re.findall(r"answer\[(\d+)\]='(\w)'", ans_script)
        answer_dict = {int(num): ans for num, ans in answers}

        return answer_dict
    

    def get_questions(self, soup: BeautifulSoup):
        # get the answers
        answer_dict = self.get_ans(soup = soup)

        if  not answer_dict:
            print("Answers not found.. This may be different page...")
            return self.data

        # Loop through all questions
        questions = soup.find_all('b')

        count = 0
        for question_tag in questions:
            q_text = question_tag.get_text(strip=True)
            count += 1 # inrese question number

            # find dot
            dot_index = q_text.find(".")

            q_num = q_text[:dot_index]
            question = q_text[dot_index + 1:] # to remove dot +1
        
            try:
                #if q_num is converted into number, means it is a number..
                q_num = int(q_num)
            except:
                q_num = count

            
            # Find options related to this question
            inputs = soup.find_all('input', {'name': f'q_{q_num}'})

            correct_option = answer_dict.get(q_num)
            if not correct_option:
                print("Question is invalid....")
                continue

            correct_option_value = f"({correct_option.upper()})"
            
            options = []
            answer = None

            for input_tag in inputs:
                option_text = input_tag.next_sibling.strip()
                options.append(option_text)

                # to get the answer as text..
                value = input_tag.get('value')
                if correct_option_value in value:
                    answer = option_text

            if not answer:
                print("Invalid answer....")
                continue
        
            # Add to list
            self.data.append({
                'question': question,
                'options': options,
                'answer': answer
            })


        return self.data
    

    def scrap_page(self, url: str):

        response = requests.get(url)
        print(response.status_code)  # Status code of the request

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # Extracting title
        title = soup.title.text
        print(f'Title: {title}')

        return self.get_questions(soup = soup)
    
    def json_data(self, data):
        return json.dumps(data, indent=4)
    
    def scrap_paper(self, url):
        response = requests.get(url)
        print(response.status_code)  # Status code of the request
        # print(response.text)

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # Extracting title
        title = soup.title.text
        print(f'Title: {title}')


        # Find all links inside the div with class 'grid-posts'
        links = soup.select('div.grid-posts a')

        if not links:
            print("This is an invalid page.....")
            return data

        # Extract and print only the URLs
        for link in links:
            url = link.get('href')
            print(f"Scrapping link : {url}")
            self.scrap_page(url = url)

        return self.data


if __name__ == "__main__":
    url = "https://www.lisquiz.com/search/label/UGC%20NET%20June%202024"

    scpr = Scrapper()
    data = scpr.scrap_paper(url = url)
    print(f"TotalQUestionsFound : {len(data)}")
    
    with open("question.json", "w") as tf:
        tf.write(scpr.json_data(data))