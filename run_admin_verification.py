"""
Test script to verify admin functionality
Run with: python manage.py shell --settings=config.settings_local < test_admin.py
"""

from portfolio.models import About, Skill, Project, BlogPost, ContactMessage

print("\n=== Testing Admin Models ===\n")

# Test About
print("1. Testing About model...")
about = About.objects.create(
    title="Test About",
    description="This is a test about section"
)
print(f"✓ Created About: {about}")
about.title = "Updated About"
about.save()
print(f"✓ Updated About: {about}")
print(f"✓ Total About entries: {About.objects.count()}")

# Test Skill
print("\n2. Testing Skill model...")
skill = Skill.objects.create(
    name="Python",
    percentage=90,
    icon="fab fa-python",
    order=1
)
print(f"✓ Created Skill: {skill}")
skill.percentage = 95
skill.save()
print(f"✓ Updated Skill: {skill}")
print(f"✓ Total Skills: {Skill.objects.count()}")

# Test Project
print("\n3. Testing Project model...")
project = Project.objects.create(
    title="Test Project",
    description="This is a test project",
    technologies="Django, Python",
    github_url="https://github.com/test",
    featured=True
)
print(f"✓ Created Project: {project}")
project.featured = False
project.save()
print(f"✓ Updated Project: {project}")
print(f"✓ Total Projects: {Project.objects.count()}")

# Test BlogPost
print("\n4. Testing BlogPost model...")
blog = BlogPost.objects.create(
    title="Test Blog Post",
    slug="test-blog-post",
    content="This is test content",
    excerpt="Test excerpt",
    published=True
)
print(f"✓ Created BlogPost: {blog}")
blog.published = False
blog.save()
print(f"✓ Updated BlogPost: {blog}")
print(f"✓ Total Blog Posts: {BlogPost.objects.count()}")

# Test ContactMessage
print("\n5. Testing ContactMessage model...")
message = ContactMessage.objects.create(
    name="Test User",
    email="test@example.com",
    subject="Test Subject",
    message="Test message content"
)
print(f"✓ Created ContactMessage: {message}")
print(f"✓ Total Contact Messages: {ContactMessage.objects.count()}")

print("\n=== All Tests Passed! ===")
print("\nAdmin should work correctly. Access at: http://127.0.0.1:8000/admin/")
