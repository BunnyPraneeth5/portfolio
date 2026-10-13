"""Seed the chat helper's answers (Phase 5b). Every row is editable in admin afterwards.

Story rows keep the original helper text unchanged but start with needs_review=True,
so they are not shown until Bunny approves them.
"""
from django.db import migrations

ANSWERS = [{'intent': 'greeting',
  'topic': 'Greeting',
  'priority': 0,
  'keywords': 'hi\n'
              'hello\n'
              'hey\n'
              'hey there\n'
              'greetings\n'
              'good morning\n'
              'good afternoon\n'
              'good evening\n'
              'namaste\n'
              'help\n'
              'can you help',
  'synonyms': 'u = you\n'
              'r = are\n'
              'ur = your\n'
              'pls = please\n'
              'plz = please\n'
              'abt = about\n'
              'wat = what\n'
              'hii = hi\n'
              'hlo = hello\n'
              'thx = thanks',
  'answer': "Hi! This is a scripted helper for {name} (Bunny)'s portfolio. It answers from the data on this "
            'site and is not an AI. Pick a topic below or type a question.',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'is_ai',
  'topic': 'Is this a bot / AI',
  'priority': 8,
  'keywords': 'are you real\n'
              'are you ai\n'
              'are you an ai\n'
              'is this ai\n'
              'is this an ai\n'
              'is this a bot\n'
              'are you a bot\n'
              'are you a robot\n'
              'are you human\n'
              'human or bot\n'
              'real person\n'
              'talking to a real person\n'
              'is this chatgpt\n'
              'chatgpt\n'
              'gpt\n'
              'who is answering\n'
              'bunny himself\n'
              'is this bunny',
  'synonyms': '',
  'answer': 'This is a scripted helper: not an AI and not Bunny in person. It matches keywords in your '
            "question and answers from Bunny's portfolio data on this site.\n"
            '\n'
            'To reach Bunny directly: {contact_email}',
  'link_label': 'Contact page',
  'link_url': '/contact/',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'who_is_bunny',
  'topic': 'Intro / about Bunny',
  'priority': 2,
  'keywords': 'tell me about yourself\n'
              'about yourself\n'
              'who is bunny\n'
              'who is karu\n'
              'karu praneeth\n'
              'who are you\n'
              'introduce\n'
              'introduction\n'
              'intro\n'
              'quick intro\n'
              'elevator pitch\n'
              'about bunny\n'
              'about him\n'
              'who is he\n'
              'summarise\n'
              'summarize\n'
              'summary of\n'
              'this candidate\n'
              'background\n'
              'bio\n'
              'about you\n'
              'who made you\n'
              'author\n'
              'creator',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'story_behind_name',
  'topic': 'Nickname "Bunny"',
  'priority': 6,
  'keywords': 'why bunny\ncalled bunny\nname bunny\nreal name\nnickname\nmeaning of bunny',
  'synonyms': '',
  'answer': "My full legal name is Karu Praneeth Kumar, and 'Bunny' is my developer handle and nickname "
            'across GitHub (BunnyPraneeth5), Kaggle, and tech communities. Feel free to call me Karu or '
            'Bunny!',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'availability',
  'topic': 'Open to roles',
  'priority': 6,
  'keywords': 'open to work\n'
              'role\n'
              'hiring for\n'
              'job opening\n'
              'interested in the role\n'
              'open to new roles\n'
              'open to roles\n'
              'open for opportunities\n'
              'open to opportunities\n'
              'opportunities\n'
              'job hunting\n'
              'looking for a job\n'
              'looking for job\n'
              'looking for work\n'
              'available for hire\n'
              'available\n'
              'availability\n'
              'hiring status\n'
              'full time\n'
              'full time roles\n'
              'contract\n'
              'permanent\n'
              'permanent position\n'
              'roles\n'
              'openings\n'
              'job search\n'
              'currently looking\n'
              'hiring',
  'synonyms': 'fte = full time\nfulltime = full time',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': True},
 {'intent': 'notice_period',
  'topic': 'Notice period / start date',
  'priority': 7,
  'keywords': 'notice period\n'
              'join\n'
              'can he join\n'
              'how soon\n'
              'how soon can he join\n'
              'join date\n'
              'joining date\n'
              'earliest joining\n'
              'joining\n'
              'start date\n'
              'when can he start\n'
              'can he start\n'
              'immediate joiner\n'
              'immediate\n'
              'when can you start',
  'synonyms': 'np = notice period\ndoj = joining date',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': True},
 {'intent': 'remote',
  'topic': 'Remote / relocation',
  'priority': 6,
  'keywords': 'remote\n'
              'remote work\n'
              'work from home\n'
              'hybrid\n'
              'on site\n'
              'onsite\n'
              'relocate\n'
              'relocation\n'
              'willing to relocate\n'
              'move to\n'
              'move cities\n'
              'shift cities\n'
              'location work',
  'synonyms': 'wfh = work from home\nwfo = on site',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': True},
 {'intent': 'internship',
  'topic': 'Internships',
  'priority': 6,
  'keywords': 'internship\nintern\nintern role\nstipend\ntrainee',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': True},
 {'intent': 'salary',
  'topic': 'Salary expectations',
  'priority': 9,
  'keywords': 'salary\n'
              'salary expectations\n'
              'ctc\n'
              'expected ctc\n'
              'current ctc\n'
              'package\n'
              'pay\n'
              'paid\n'
              'compensation\n'
              'how much does he want',
  'synonyms': 'lpa = salary\npkg = package\nsal = salary',
  'answer': 'Salary is discussed directly with Bunny. Please get in touch at {contact_email}.',
  'link_label': 'Contact page',
  'link_url': '/contact/',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'work_authorization',
  'topic': 'Work authorization / visa',
  'priority': 9,
  'keywords': 'visa\n'
              'sponsorship\n'
              'visa sponsorship\n'
              'work permit\n'
              'authorized to work\n'
              'authorised to work\n'
              'work authorization\n'
              'work authorisation\n'
              'work in the us\n'
              'work in us',
  'synonyms': '',
  'answer': 'Please confirm work authorization directly with Bunny at {contact_email}.',
  'link_label': 'Contact page',
  'link_url': '/contact/',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'other_offers',
  'topic': 'Other interviews / offers',
  'priority': 9,
  'keywords': 'other offers\n'
              'offers in hand\n'
              'competing offers\n'
              'interviewing elsewhere\n'
              'interviewing anywhere else\n'
              'other interviews\n'
              'other companies',
  'synonyms': '',
  'answer': "That's best discussed with Bunny directly. Please get in touch at {contact_email}.",
  'link_label': 'Contact page',
  'link_url': '/contact/',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'leading_questions',
  'topic': 'Leading / pressure questions',
  'priority': 9,
  'keywords': 'planning to leave\n'
              'leave his company\n'
              'leave his job\n'
              'quit his job\n'
              'quit\n'
              'guarantee\n'
              'promise\n'
              'will he accept\n'
              'would he accept',
  'synonyms': '',
  'answer': "This helper can't speak for Bunny on that. Please ask Bunny directly at {contact_email}.",
  'link_label': 'Contact page',
  'link_url': '/contact/',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'resume',
  'topic': 'Resume',
  'priority': 5,
  'keywords': 'resume\ndownload resume\nresume pdf\npdf\nshare resume\nlatest cv',
  'synonyms': 'cv = resume\nc v = resume\nbiodata = resume',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'contact',
  'topic': 'Contact / location / GitHub',
  'priority': 4,
  'keywords': 'contact\n'
              'email\n'
              'mail\n'
              'reach him\n'
              'reach you\n'
              'reach out\n'
              'how do i reach\n'
              'get in touch\n'
              'linkedin\n'
              'phone\n'
              'phone number\n'
              'call him\n'
              'where is bunny based\n'
              'based\n'
              'location\n'
              'current location\n'
              'which city\n'
              'address\n'
              'bengaluru\n'
              'kurnool\n'
              'github\n'
              'github link\n'
              'see his code\n'
              'his code\n'
              'source code',
  'synonyms': 'gh = github\nph = phone\nmob = phone',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'schedule_interview',
  'topic': 'Schedule an interview',
  'priority': 6,
  'keywords': 'schedule\n'
              'schedule an interview\n'
              'interview\n'
              'set up a call\n'
              'schedule a call\n'
              'book a meeting\n'
              'meeting\n'
              'book a call',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'education',
  'topic': 'Education / graduation',
  'priority': 4,
  'keywords': 'education\n'
              'college\n'
              'university\n'
              'degree\n'
              'study\n'
              'studied\n'
              'what did he study\n'
              'gpa\n'
              'cgpa\n'
              'major\n'
              'sjcet\n'
              'btech\n'
              'b tech\n'
              'coursework\n'
              'academic\n'
              'graduate\n'
              'graduation\n'
              'passing out\n'
              'passing out year\n'
              'batch\n'
              'cse',
  'synonyms': 'passout = passing out\npass out = passing out\ngrad = graduate',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'fresher_or_experienced',
  'topic': 'Fresher or experienced',
  'priority': 6,
  'keywords': 'fresher\nexperienced or fresher\nfresh graduate\nfresh grad\nentry level',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'current_role',
  'topic': 'Current role',
  'priority': 6,
  'keywords': 'working now\n'
              'where is he working\n'
              'current company\n'
              'current role\n'
              'current job\n'
              'present employer\n'
              'employer\n'
              'what does he do currently\n'
              'currently working\n'
              'does currently',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'experience',
  'topic': 'Work experience / leadership',
  'priority': 1,
  'keywords': 'experience\n'
              'where have you worked\n'
              'have you worked\n'
              'where do you work\n'
              'work experience\n'
              'professional experience\n'
              'work history\n'
              'worked at\n'
              'has he worked at\n'
              'worked at any company\n'
              'where has he worked\n'
              'where did he work\n'
              'where did you work\n'
              'internship done\n'
              'internship history\n'
              'past internship\n'
              'previous internship\n'
              'your internship\n'
              'his internship\n'
              'years of experience\n'
              'hackathon\n'
              'leadership\n'
              'leadership roles\n'
              'led\n'
              'led any\n'
              'team or event\n'
              'techtrotter\n'
              'event\n'
              'your experience\n'
              'internship experience\n'
              'previous role',
  'synonyms': 'yoe = years of experience\nexp = experience\nworkex = work experience',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'certifications',
  'topic': 'Certifications',
  'priority': 5,
  'keywords': 'certification\ncertificate\ncertified\ncredentials\ncourse\ncourses\nmcp certified',
  'synonyms': 'certs = certifications\ncert = certification',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'skills_general',
  'topic': 'Skills overview',
  'priority': 3,
  'keywords': 'skills\n'
              'coding\n'
              'good at coding\n'
              'skill\n'
              'tech stack\n'
              'stack\n'
              'technologies\n'
              'what languages\n'
              'programming languages\n'
              'toolkit\n'
              'tools\n'
              'frameworks\n'
              'technical skills\n'
              'database\n'
              'databases\n'
              'sql\n'
              'postgres\n'
              'mysql\n'
              'docker\n'
              'kubernetes\n'
              'cloud\n'
              'deployed\n'
              'deploy\n'
              'aws\n'
              'gcp\n'
              'azure\n'
              'devops\n'
              'git\n'
              'what do you know',
  'synonyms': 'k8s = kubernetes\ndb = database',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'skill_python',
  'topic': 'Python',
  'priority': 5,
  'keywords': 'python',
  'synonyms': 'py = python',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'skill_ml',
  'topic': 'Machine learning',
  'priority': 5,
  'keywords': 'machine learning\n'
              'deep learning\n'
              'trained models\n'
              'train models\n'
              'model training\n'
              'tensorflow\n'
              'pytorch\n'
              'scikit\n'
              'scikit learn\n'
              'keras\n'
              'nlp\n'
              'neural network\n'
              'feature engineering',
  'synonyms': 'ml = machine learning\ndl = deep learning',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'skill_agentic',
  'topic': 'Agentic AI / MCP / LLMs',
  'priority': 5,
  'keywords': 'agentic\n'
              'agentic ai\n'
              'ai agents\n'
              'agent\n'
              'agents\n'
              'mcp\n'
              'model context protocol\n'
              'multi agent\n'
              'multi agent systems\n'
              'autonomous agent\n'
              'tool use\n'
              'llm\n'
              'large language model\n'
              'rag\n'
              'rag pipeline\n'
              'langchain\n'
              'llamaindex\n'
              'langgraph\n'
              'crewai\n'
              'autogen\n'
              'vector database\n'
              'embeddings',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'skill_django',
  'topic': 'Backend / APIs',
  'priority': 5,
  'keywords': 'django\ndrf\nbackend\nback end\nrest api\napi\napis\nflask\nfastapi\ndjango rest framework',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'skill_web',
  'topic': 'Frontend / web',
  'priority': 5,
  'keywords': 'web\n'
              'frontend\n'
              'front end\n'
              'react\n'
              'html\n'
              'css\n'
              'javascript\n'
              'fullstack\n'
              'full stack\n'
              'nextjs\n'
              'tailwind',
  'synonyms': 'js = javascript',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'skill_security',
  'topic': 'Security',
  'priority': 5,
  'keywords': 'security\n'
              'cybersecurity\n'
              'cyber security\n'
              'soc\n'
              'siem\n'
              'threat\n'
              'threat intel\n'
              'threat intelligence\n'
              'intrusion\n'
              'penetration\n'
              'vulnerability\n'
              'pentest',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'coding_profiles',
  'topic': 'Coding profiles',
  'priority': 6,
  'keywords': 'leetcode\n'
              'hackerrank\n'
              'codechef\n'
              'codeforces\n'
              'competitive programming\n'
              'dsa\n'
              'coding profile\n'
              'coding practice',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'research_kaggle',
  'topic': 'Kaggle / research',
  'priority': 6,
  'keywords': 'kaggle\nresearch\nresearch experience\npublished\npapers\npublications',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'projects_general',
  'topic': 'Projects overview',
  'priority': 3,
  'keywords': 'projects\n'
              'portfolio link\n'
              'project\n'
              'built\n'
              'what has he built\n'
              'show me his work\n'
              'see his work\n'
              'portfolio projects\n'
              'portfolio project\n'
              'case studies\n'
              'recent work\n'
              'live demo\n'
              'demo\n'
              'try any of his projects\n'
              'deployed projects\n'
              'can i try',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'flagship',
  'topic': 'Best project',
  'priority': 6,
  'keywords': 'best project\nmost impressive\nflagship\nlook at first\ntop project\nstrongest project',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'specific_project',
  'topic': 'A project by name (matched from project titles and tags)',
  'priority': 0,
  'keywords': '',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'soc_copilot',
  'topic': 'SOC Copilot',
  'priority': 7,
  'keywords': 'soc copilot\nsoc project\nsoc thing\ncicids\ncicids2017\nshodan\nintrusion detection project',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'car_sales',
  'topic': 'Car price prediction',
  'priority': 7,
  'keywords': 'car sales\n'
              'car price\n'
              'car price prediction\n'
              'price prediction\n'
              'car sales model\n'
              'neural network project',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'gate_pass',
  'topic': 'College gate pass',
  'priority': 7,
  'keywords': 'gate pass\ngate pass system\nqr gate pass\nqr code\ncollege gate\naccess control',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'replay',
  'topic': 'Recorded agent replays',
  'priority': 7,
  'keywords': 'replay\n'
              'agent in action\n'
              'agent running\n'
              'see an agent\n'
              'demo of the agent\n'
              'recorded run\n'
              'watch the agent',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'site_tech',
  'topic': 'How this site is built',
  'priority': 6,
  'keywords': 'this website\nthis site\nwebsite built\nsite built\nbuilt with\nsite made\nthis portfolio',
  'synonyms': '',
  'answer': 'This site is built with Django, plain HTML and CSS, and vanilla JavaScript. The chat helper is '
            "rule-based: it matches keywords and answers from the site's own data.",
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'why_hire',
  'topic': 'Why hire / strengths',
  'priority': 5,
  'keywords': 'why should we hire\n'
              'why hire\n'
              'hire him\n'
              'why him\n'
              'why pick him\n'
              'pick him\n'
              'makes him different\n'
              'what makes him different\n'
              'strengths\n'
              'strength\n'
              'superpower\n'
              'secret sauce\n'
              'best at\n'
              'convince me\n'
              'sets him apart\n'
              'what sets you apart\n'
              'value proposition\n'
              'competitive advantage\n'
              'why choose\n'
              'why you',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'hardest_bug',
  'topic': 'Hardest bug',
  'priority': 6,
  'keywords': 'hardest bug\n'
              'challenging bug\n'
              'hardest problem\n'
              'tough bug\n'
              'toughest bug\n'
              'difficult bug\n'
              'toughest problem\n'
              'technical problem\n'
              'debugging\n'
              'debugging challenge\n'
              'obstacle\n'
              'challenge',
  'synonyms': '',
  'answer': 'The hardest bug I encountered was managing async state synchronization and preventing deadlocks '
            "in SOC Copilot's 4-agent MCP pipeline. Because multiple agents (Recon, Reputation, Shodan) were "
            'returning data concurrently, updating the PyQt6 GUI directly caused race conditions. I resolved '
            'it by designing a thread-safe signal dispatcher and decoupling task execution into an async '
            'queue with strict state locking.',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'why_agentic_over_llm',
  'topic': 'Why agentic AI over plain LLMs',
  'priority': 6,
  'keywords': 'agentic vs llm\n'
              'why mcp\n'
              'why agents\n'
              'chatbot vs agent\n'
              'traditional chatbot\n'
              'fine tuned llm\n'
              'static prompt',
  'synonyms': '',
  'answer': 'Traditional LLMs and static chatbots generate single-shot text predictions, making them prone '
            'to hallucinations when tackling complex tasks. Agentic AI with Model Context Protocol (MCP) '
            'gives models agency—allowing them to dynamically select tools, query databases, invoke APIs '
            '(like Shodan), and self-correct across steps. It transforms an AI model from a passive text box '
            'into an active software agent.',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'agent_failure_handling',
  'topic': 'Agent failures / guardrails',
  'priority': 6,
  'keywords': 'agent stuck\n'
              'gets stuck\n'
              'stuck in a loop\n'
              'agent error\n'
              'agent fail\n'
              'hallucination\n'
              'infinite loop\n'
              'fallback\n'
              'guardrail\n'
              'error handling',
  'synonyms': '',
  'answer': 'To prevent AI agents from looping or getting stuck, I implement deterministic guardrails: '
            'maximum step limits, strict Pydantic/JSON schema validation on tool calls, and fallback '
            'exception handlers. If an agent receives unparseable API output, it catches the error '
            'gracefully, injects context-specific correction prompts, or escalates to a human-in-the-loop '
            'callback.',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'explain_to_ceo',
  'topic': 'Explain simply',
  'priority': 6,
  'keywords': 'explain to non technical\n'
              'explain to ceo\n'
              'layman terms\n'
              'layman\n'
              'simple terms\n'
              'non technical\n'
              'not technical\n'
              'explain soc copilot\n'
              'explain simply',
  'synonyms': '',
  'answer': "If I were explaining SOC Copilot to a non-technical executive, I'd say: Imagine having a "
            'digital security squad of 4 specialized AI analysts working 24/7. One watches the door, one '
            'investigates suspicious IPs, one checks global vulnerability threat feeds, and one writes '
            'concise executive briefings—giving you instant security triage in seconds.',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'fun_curiosity_project',
  'topic': 'Side projects',
  'priority': 6,
  'keywords': 'fun project\ncuriosity\nside project\nfun side project\nweekend project\npet project\nfor fun',
  'synonyms': '',
  'answer': 'One of my favorite curiosity projects was building an interactive desktop companion widget in '
            'PyQt6 with custom vector animations. I wanted to see how seamlessly I could bridge desktop OS '
            'events with dynamic web APIs and local LLM micro-agents.',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'rearchitect_project',
  'topic': 'What would he redo',
  'priority': 6,
  'keywords': 're architect\n'
              'rearchitect\n'
              'do differently\n'
              'would he do differently\n'
              'what would you change\n'
              'what would change\n'
              'improve project\n'
              'rebuilt\n'
              'rebuild\n'
              'regrets',
  'synonyms': '',
  'answer': 'If I were re-architecting SOC Copilot from scratch today, I would upgrade the agent '
            'communication layer from local thread queues to an event-driven Redis pub/sub message broker '
            'with WebSocket streaming. That would allow individual MCP agents to scale horizontally across '
            'distributed cloud containers rather than running on a single host.',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'conflict_disagreement',
  'topic': 'Teamwork / conflict',
  'priority': 6,
  'keywords': 'disagreement\n'
              'conflict\n'
              'differing opinion\n'
              'team argument\n'
              'argument\n'
              'collaborate\n'
              'disagree\n'
              'disagreed\n'
              'handle conflict',
  'synonyms': '',
  'answer': 'During TechTrotter 2K25, when team members had conflicting ideas on technical architecture '
            'under tight hackathon deadlines, I brought everyone together to build rapid 15-minute '
            'benchmarks and test assumptions with real sample inputs. Data-driven evidence quickly resolved '
            'opinions and kept the team focused on building the best solution.',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'stay_updated',
  'topic': 'Staying updated',
  'priority': 6,
  'keywords': 'stay updated\nkeep up\nkeeps up\nlearn new\nlearn new tech\nlatest ai\ntrends',
  'synonyms': '',
  'answer': 'I stay ahead of rapid AI developments by regularly reading arXiv preprints, following the Model '
            'Context Protocol (MCP) and multi-agent open-source ecosystems on GitHub, building hands-on '
            'weekend prototypes, and competing in ML challenges on Kaggle.',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'tight_deadlines',
  'topic': 'Tight deadlines',
  'priority': 6,
  'keywords': 'tight deadline\ndeadline\npressure\nunder pressure\nfast paced\nquick turn\nfast turn',
  'synonyms': '',
  'answer': 'I thrive under tight deadlines! Leading TechTrotter 2K25 taught me how to ruthlessly prioritize '
            'core MVP capabilities, delegate effectively, and deliver reliable, high-performing software on '
            'tight schedules without compromising code architecture.',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'startup_vs_senior',
  'topic': 'Junior vs senior',
  'priority': 6,
  'keywords': 'startup vs senior\nwhy junior\nwhy fresh\nfresher vs\nsenior engineer\nfresh graduate vs',
  'synonyms': '',
  'answer': 'Why hire me for a startup? I bring specialized, hands-on expertise in bleeding-edge '
            'technologies like Agentic AI and MCP—frameworks that emerged very recently—with zero legacy '
            "debt mindset. I'm agile, build full-stack prototypes fast, and am ready to start immediately "
            'with maximum drive.',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'fav_library',
  'topic': 'Favourite tools',
  'priority': 6,
  'keywords': 'favorite library\n'
              'favourite library\n'
              'fav library\n'
              'favorite framework\n'
              'favourite framework\n'
              'fav framework\n'
              'go to framework\n'
              'tool of choice\n'
              'favorite tool\n'
              'favourite tool',
  'synonyms': '',
  'answer': 'My favorite Python libraries are PyTorch and Django. PyTorch offers total flexibility for '
            'designing dynamic ML computational graphs, while Django provides a clean, battery-included '
            'architecture for shipping secure production web backends rapidly.',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'bias_bad_data',
  'topic': 'Messy / imbalanced data',
  'priority': 6,
  'keywords': 'dataset bias\n'
              'bad data\n'
              'imbalanced data\n'
              'imbalanced\n'
              'data quality\n'
              'cleaning data\n'
              'data cleaning\n'
              'pre processing\n'
              'preprocessing\n'
              'smote',
  'synonyms': '',
  'answer': 'In domain datasets like intrusion detection (CICIDS2017), normal network traffic vastly '
            'outnumbers attack records. I handle data imbalance and noise using SMOTE oversampling, feature '
            'normalization, stratification, and evaluating models with Precision-Recall AUC and Confusion '
            'Matrices rather than relying on misleading raw accuracy.',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'replace_developers',
  'topic': 'AI replacing developers',
  'priority': 6,
  'keywords': 'replace developers\nreplace humans\ntake our jobs\nai replacing\nai replace',
  'synonyms': '',
  'answer': "AI agents won't replace software engineers; they are massive productivity multipliers! Agents "
            'eliminate repetitive boilerplate, manual log inspection, and routine triage, allowing engineers '
            'to focus on high-level system architecture, creative problem solving, and product strategy.',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'system_design',
  'topic': 'System design',
  'priority': 6,
  'keywords': 'system design\narchitecture\nscalability\nscalable\nmicroservices\ndesign approach',
  'synonyms': '',
  'answer': 'My approach to system design centers on modularity, clean interface boundaries, and '
            'single-responsibility components. Whether building an MCP multi-agent pipeline or a Django REST '
            'backend, I decouple data storage, business logic, and API presentation to ensure long-term '
            'scalability and easy testing.',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'walle_fun',
  'topic': 'WALL-E fun answer',
  'priority': 6,
  'keywords': 'directive\neva\nwall e\nwalle\nfavorite movie\nfavourite movie',
  'synonyms': '',
  'answer': 'I love building high-tech interfaces and intelligent agent pipelines! In my free time, I enjoy '
            'exploring new AI research papers, tweaking UI animations, and experimenting with autonomous '
            "micro-agents. Try asking me about 'SOC Copilot' or 'Why Agentic AI'!",
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'failure',
  'topic': 'Failure / mistakes',
  'priority': 6,
  'keywords': 'failed\nfailure\na time he failed\nmistake\nbiggest mistake\nwent wrong',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'weakness',
  'topic': 'Weakness',
  'priority': 6,
  'keywords': 'weakness\nbiggest weakness\nareas of improvement\narea of improvement\nbad at',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'why_ai',
  'topic': 'Why AI',
  'priority': 6,
  'keywords': 'why ai\n'
              'choose ai\n'
              'why did he choose ai\n'
              'got him into\n'
              'why machine learning\n'
              'why agentic ai\n'
              'why this field\n'
              'motivation',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'career_goals',
  'topic': 'Career goals',
  'priority': 6,
  'keywords': '5 years\nfive years\ncareer goals\nlong term\nfuture goals\nwant to do next\nsee himself',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'open_source',
  'topic': 'Open source',
  'priority': 6,
  'keywords': 'open source\nopen source contributions\ncontributed to open source\ncontributions',
  'synonyms': 'oss = open source',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'backlogs',
  'topic': 'Backlogs / gaps',
  'priority': 6,
  'keywords': 'backlog\nbacklogs\narrears\narrear\ngap year\ngap years\neducation gap\ngap in education',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'service_bond',
  'topic': 'Service bond',
  'priority': 6,
  'keywords': 'bond\nservice bond\nyear bond\nservice agreement\nsign a bond',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'shifts_timezone',
  'topic': 'Shifts / time zone',
  'priority': 6,
  'keywords': 'night shift\n'
              'night shifts\n'
              'shifts\n'
              'rotational shifts\n'
              'us hours\n'
              'time zone\n'
              'timezone\n'
              'odd hours\n'
              'weekend work',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'company_preference',
  'topic': 'Startup / product / service preference',
  'priority': 6,
  'keywords': 'startup\n'
              'startups\n'
              'interested in startups\n'
              'product company\n'
              'service company\n'
              'product or service\n'
              'mnc\n'
              'mnc or startup',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'languages_spoken',
  'topic': 'Spoken languages',
  'priority': 6,
  'keywords': 'languages does he speak\n'
              'speak\n'
              'speaks\n'
              'spoken languages\n'
              'hindi\n'
              'telugu\n'
              'english fluency\n'
              'fluency\n'
              'fluent',
  'synonyms': '',
  'answer': '',
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': True,
  'follows_job_search_mode': False},
 {'intent': 'fallback',
  'topic': 'Reply when nothing matches',
  'priority': 0,
  'keywords': '',
  'synonyms': '',
  'answer': "Sorry, I didn't catch that. Try one of these topics:",
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False},
 {'intent': 'pending_review',
  'topic': 'Reply for topics without an approved answer',
  'priority': 0,
  'keywords': '',
  'synonyms': '',
  'answer': "There's no approved answer for that yet. Here are topics this helper can answer:",
  'link_label': '',
  'link_url': '',
  'is_active': True,
  'needs_review': False,
  'follows_job_search_mode': False}]


def seed(apps, schema_editor):
    ChatAnswer = apps.get_model('portfolio', 'ChatAnswer')
    for row in ANSWERS:
        ChatAnswer.objects.update_or_create(intent=row['intent'], defaults=row)


def unseed(apps, schema_editor):
    ChatAnswer = apps.get_model('portfolio', 'ChatAnswer')
    ChatAnswer.objects.filter(intent__in=[row['intent'] for row in ANSWERS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0025_chat_answers_and_job_search_mode'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
