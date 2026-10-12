from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from portfolio.models import Project, ProjectReplay
from portfolio.replays import ReplayValidationError, load_replay_file


class Command(BaseCommand):
    help = 'Import a sanitized replay JSON file for a project (same checks as the admin upload).'

    def add_arguments(self, parser):
        parser.add_argument('project_slug')
        parser.add_argument('path')
        parser.add_argument('--title', help='Override the title from the file.')
        parser.add_argument('--order', type=int, default=0)
        parser.add_argument('--publish', action='store_true', help='Publish immediately (default: unpublished).')
        parser.add_argument('--feature-on-home', action='store_true', help='Play this replay first on the homepage.')

    def handle(self, *args, **options):
        try:
            project = Project.objects.get(slug=options['project_slug'])
        except Project.DoesNotExist:
            raise CommandError(f"No project with slug '{options['project_slug']}'.")

        path = Path(options['path'])
        if not path.is_file():
            raise CommandError(f'File not found: {path}')

        try:
            doc = load_replay_file(path.read_bytes())
        except ReplayValidationError as err:
            raise CommandError('Replay rejected:\n  - ' + '\n  - '.join(err.messages))

        replay = ProjectReplay(
            project=project,
            title=options['title'] or doc['title'],
            duration_s=doc['duration_s'],
            steps=doc['steps'],
            order=options['order'],
            is_published=options['publish'],
            is_featured_on_home=options['feature_on_home'],
        )
        try:
            replay.full_clean()
        except ValidationError as err:
            messages = [f'{field}: {msg}' for field, msgs in err.message_dict.items() for msg in msgs]
            raise CommandError('Replay rejected:\n  - ' + '\n  - '.join(messages))
        replay.save()

        state = 'published' if replay.is_published else 'NOT published (publish it in admin after checking)'
        self.stdout.write(self.style.SUCCESS(
            f"Imported replay '{replay.title}' ({replay.step_count} steps, {replay.duration_label}) "
            f"for '{project.title}' as id {replay.pk}; {state}."
        ))
