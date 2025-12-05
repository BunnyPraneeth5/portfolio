import os

templates = ['skills.html', 'projects.html', 'blog.html', 'blog_detail.html']
replacements = [
    ('href="index.html"', 'href="{% url \'index\' %}"'),
    ('href="about.html"', 'href="{% url \'about\' %}"'),
    ('href="skills.html"', 'href="{% url \'skills\' %}"'),
    ('href="projects.html"', 'href="{% url \'projects\' %}"'),
    ('href="blog.html"', 'href="{% url \'blog\' %}"'),
    ('href="contact.html"', 'href="#"'),
]

for template in templates:
    path = f'templates/{template}'
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        for old, new in replacements:
            content = content.replace(old, new)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated {template}')
