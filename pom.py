#!/usr/bin/python

import json
import os
import shutil
import sys

from bs4 import BeautifulSoup
import dateparser
from jinja2 import Environment, FileSystemLoader
import markdown
from slugify import slugify



file_loader = FileSystemLoader("templates")
env = Environment(loader=file_loader)


divider = "ʕ •ᴥ•ʔ"
config = {}
not_episodes = []
episodes = []


def get_related(target_episode):
    related_pages = []
    tags = set(target_episode["header"]["tags"])
    for i, each in enumerate(episodes):
        if target_episode["header"]["title"] is each["header"]["title"]:
            continue
        target_tags = set(each["header"]["tags"])
        shared_tags = tags.intersection(target_tags)
        t = {}
        t["score"] = len(shared_tags)
        if t["score"] > 0:
            t["title"] = each["header"]["title"]
            t["url"] = each["url"]
            #t["datetime"] = each["datetime"]
            related_pages.append(t)
    related_pages = sorted(related_pages, key=lambda i: i["score"], reverse=True)[:5]
    return related_pages

def render_html(body, header):
    template = env.get_template('page.html')
    output = template.render(config=config, body=body, header=header)
    output = BeautifulSoup(output, 'html.parser').prettify(formatter="html5")
    return output



if __name__ == "__main__":
    try:
        config_path = sys.argv[1]
    except IndexError:
        print("arg required")
        exit()
    if not os.path.exists(config_path):
        print("File Doesn't Exist: " + config_path)
        exit()
    with open(config_path) as f:
        config = json.load(f)
    if not os.path.isdir(config["content_dir"]):
        print("Content directory doesn't exist: " + config["content_dir"])
        exit()
    if not os.path.isdir(config["output_dir"]):
        print("Output directory doesn't exist: " + config["output_dir"])
        exit()
    
    content_files = []
    
    for (dirpath, dirnames, filenames) in os.walk(config['content_dir']):
        content_files.extend(filenames)    
    

    pages = []
    for each in content_files:
        page = {}
        page['content_path'] = os.path.join(config["content_dir"], each)
        with open(page['content_path']) as f:
            data = f.read()
        [header, page['body']] = data.split(divider)
        
        page['body'] = page['body'].strip()
        page['body'] = markdown.markdown(page['body'])

        page['header'] = json.loads(header)
        if 'date' in  page['header']:
            page['header']['datetime'] = dateparser.parse(page['header']['date'])
            page['header']['date_str'] = page['header']['datetime'].strftime("%B %-d, %Y")
        if 'slug' in page['header']:
            page['slug'] =  page['header']['slug']
        else:
            page['slug'] = slugify(page['header']['title'])
        page['url'] = config['base_url'] + '/' + page['slug']
        page['dir'] = os.path.join(config["output_dir"], page['slug'])
        page['path'] = os.path.join(page['dir'], 'index.html')

        if 'tags' not in  page['header']:
            page['header']['tags'] = []

        if 'date' in  page['header']:
            episodes.append(page)
        else:
            not_episodes.append(page)
    
    episodes = sorted(episodes, key = lambda i: i['header']['datetime'], reverse=True)



    for target_episode in episodes:
        #print(target_episode['header']['title'])
        target_episode['related'] = get_related(target_episode)

    home = {}
    home['homepage'] = True
    home['url'] = config['base_url']
    home['path'] = '/'
    home['header'] = {}
    home['slug'] = None 
    home['dir'] = os.path.join(config["output_dir"],)
    home['path'] = os.path.join(home['dir'], 'index.html')

    not_episodes.append(home)

    for page in (episodes + not_episodes):

        if page['slug'] == 'episodes':
            episode_list = env.get_template('episode_list.html')
            output = episode_list.render(episodes=episodes)
            page['body']  = page['body'] + output

        template = env.get_template('page.html')
        output = template.render(config=config, page=page)

        if not os.path.exists(page['dir']):
            os.makedirs(page['dir'])
        with open(page['path'], 'w') as f:
            f.write(output)

        template = env.get_template('page.html')
        output = template.render(config=config, page=page)

        
   
    sitemap_path = os.path.join(config["output_dir"], 'sitemap.txt')
    sitemap = open(sitemap_path, "w")

    for page in (episodes + not_episodes):
        print(page['url'])
        sitemap.write(page['url'] + "\n")
    sitemap.close()


    robot_path = os.path.join(config["output_dir"], 'robots.txt')
    template = env.get_template('robots.txt')
    output = template.render()
    with open(robot_path, 'w') as f:
        f.write(output)






    
  
    

        

exit()
def load_content(content_dir):
    content_files = []
    for (dirpath, dirnames, filenames) in os.walk(content_dir):
        content_files.extend(filenames)
    



def render_page(content_file):
    f = open(content_file, "r")
    data = f.read()
    [header, body] = data.split(divider)
    header = json.loads(header)
    if 'date' in header:
        header['date_str'] = dateparser.parse(header['date']).strftime("%B %-d, %Y")
    body = body.strip()
    body = markdown.markdown(body)
    output = render_html(body, header)


def render_home():
    file_path = os.path.join(config["output_dir"], "index.html")
    header = {}
    body = ''
    body = body.strip()
    body = markdown.markdown(body)
    output = render_html(body, header)
    with open(file_path, 'w') as f:
        f.write(output)



content_files = load_content(config["content_dir"])
render_home()
exit()
for each in content_files:
    render_page(os.path.join(config["content_dir"], each))
