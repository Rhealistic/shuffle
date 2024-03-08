import signal
import sys
import time
import traceback

from django.core.management.base import BaseCommand
from django.utils import timezone
from shuffle.artist.models import Opportunity
from shuffle.artist.utils.discovery import discover_opportunities
from shuffle.curator.models import Concept
from shuffle.curator.utils.invites import fetch_expired_shuffle_invites

from shuffle.curator.utils.shuffle import do_reshuffle, do_shuffle, fetch_latest_pending_shuffles

class Command(BaseCommand):
    help = 'Run JOBS!'

    def add_arguments(self, parser):
        parser.add_argument(
            '--job',
            type=str,
            choices=['shuffle', 'expired-invites', 'discovery'],
            help='Specify the job to run'
        )

    def run_shuffle(self):
        self.stdout.write(self.style.NOTICE(f'{timezone.now()}: Processing shuffles ---'))

        shuffles = fetch_latest_pending_shuffles()
        self.stdout.write(self.style.NOTICE(f'{timezone.now()}: Found {shuffles.count()} pending shuffles found ---'))

        for shuffle in shuffles:
            self.stdout.write(self.style.NOTICE(f'{timezone.now()}: Processing shuffle `{shuffle.shuffle_id}` ---'))

            start_time = time.time()
            do_shuffle(shuffle)

            end_time = time.time()
            self.stdout.write(self.style.NOTICE(f"Script execution time: {(end_time - start_time) / 60} minutes"))

    def handle_expired_invites(self):
        self.stdout.write(self.style.NOTICE(f'{timezone.now()}: Processing expired invites ---'))

        expired_opportunities = fetch_expired_shuffle_invites()
        self.stdout.write(self.style.NOTICE(f'{timezone.now()}: Found {expired_opportunities.count()} expired invites ---'))

        for opportunity in expired_opportunities:
            self.stdout.write(self.style.NOTICE(f'{timezone.now()}:  Processing shuffle `{opportunity.opportunity_id}` ---'))

            start_time = time.time()
            do_reshuffle(opportunity, Opportunity.Status.EXPIRED)

            end_time = time.time()
            self.stdout.write(self.style.NOTICE(f"Script execution time: {(end_time - start_time) / 60} minutes"))

    def run_discovery(self):
        self.stdout.write(self.style.NOTICE(f'{timezone.now()}: Processing opportunity discovery ---'))

        start_time = time.time()
        for concept in Concept.objects.filter(is_active=True):
            discover_opportunities(concept)

        end_time = time.time()
        self.stdout.write(self.style.NOTICE(f"Script execution time: {(end_time - start_time) / 60} minutes"))

    def handle(self, *args, **options):
        job = options.get('job')
        
        # Your script logic here
        self.stdout.write(self.style.NOTICE(f'{timezone.now()}: Running jobs! ---'))

        try:
            if job == "shuffle":
                self.run_shuffle()
                self.stdout.write(self.style.SUCCESS(f'{timezone.now()}: Script executed successfully ---'))
            elif job == 'expired-invites':
                self.handle_expired_invites()
                self.stdout.write(self.style.SUCCESS(f'{timezone.now()}: Script executed successfully ---'))
            elif job == 'discovery':
                self.run_discovery()
                self.stdout.write(self.style.SUCCESS(f'{timezone.now()}: Script executed successfully ---'))
            else:
                self.stdout.write(self.style.WARNING(f'{timezone.now()}: No valid job specified'))
                self.stdout.write(self.style.SUCCESS(f'{timezone.now()}: Script executed successfully ---'))

        except KeyboardInterrupt:
            self.stdout.write(self.style.ERROR(f'{timezone.now()}: Exiting abruptly'))
            cleanup_and_exit(signal.SIGINT, None)

        except Exception as e:
            exc_type, exc_value, _ = sys.exc_info()
            print(traceback.format_exc())

            self.stdout.write(self.style.ERROR(f'{timezone.now()}: Exception Type: {exc_type} ---'))
            self.stdout.write(self.style.ERROR(f'{timezone.now()}: Exception Value: {exc_value} ---'))


def cleanup_and_exit(signum, frame):
    print(f"Crtl+C pressed. performing cleanup... Exiting. ---", signum, frame)
    sys.exit(0)


signal.signal(signal.SIGTERM, cleanup_and_exit)
signal.signal(signal.SIGINT, cleanup_and_exit)
