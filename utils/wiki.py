import wikipediaapi
import html
import re



def retrieve_page(keyword):
    wiki_wiki = wikipediaapi.Wikipedia('en', extract_format=wikipediaapi.ExtractFormat.HTML)
    wiki_page = wiki_wiki.page(keyword)
    if wiki_page.exists():
        summary = wiki_page.summary
        text = wiki_page.text
        # clean summary
        plain_summary = re.sub(r'<[^>]*>', '', summary)
        return plain_summary, text



def render_wiki_html(text, keyword):
    # render html here
    with open('template01.html', 'r') as f:
        html_template = f.read()
    escaped_text = html.escape(text)
    html_page = html_template.format(html.unescape(escaped_text))
    with open(f'{keyword}_wiki.html', 'w') as f:
        f.write(html_page)
    return f'{keyword}_wiki.html'



