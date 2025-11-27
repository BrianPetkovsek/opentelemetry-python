twiggy
opened on Mar 17, 2024
Describe your environment
celery running using "multi" in systemd service file which forks workers. also using solarwinds opentelemetry wrapper which complicates it a bit more. this might trace back to them a bit, but I do think the issue lies more with otel and celery multi ( forking ). I wasn't sure if I should submit this bug report to celery, otel, or solarwinds, but kind of seems like all three.

these celery doc files might help explain what I mean by "multi"
https://docs.celeryq.dev/en/stable/reference/celery.bin.multi.html
https://docs.celeryq.dev/en/stable/userguide/daemonizing.html#usage-systemd

Steps to reproduce
run opentelemetry-instrument celery -A tasks multi start worker --concurrency=10 or a similar setup......

What is the expected behavior?
trace as normal

What is the actual behavior?
only a few traces during initial startup, but nothing about celery tasks, database, etc. suspect that the new forked process is unaware that it was launched with opentelemetry-instrumentation ( ie. opentelemetry.instrumentation.auto_instrumentation )

Additional context
running opentelemetry-instrument celery -A tasks worker --concurrency=10 and using Type=simple vs forking allows this to work. this means that systemd sort of fires and forgets celery starting up, which is an okay compromise workaround, but it may make it harder to detect that the service doesn't start properly. monitoring celery/services uptime on linux is a bigger fish anyways.

an ex .service file for reference that works around the issue

Description=celeryman-worker
After=network.target

[Service]
Type=simple
User=deployer
Group=deployer
WorkingDirectory=/opt/c3p0/celery/celeryman
RuntimeDirectory=celery
Environment="SW_APM_CONFIG_FILE=./solarwinds-apm-config.json"
ExecStart=/opt/pyenv/celeryman_py/env/bin/celery -A tasks worker --loglevel=info --logfile=/opt/logging/celery.log --concurrency=10

[Install]
WantedBy=multi-user.target
This is probably something like the issues with Gunicorn where processes fork and using opentelemetry-instrument as a shell wrapper won't cut it. https://opentelemetry-python.readthedocs.io/en/latest/examples/fork-process-model/README.html

I've tried the solution mentioned on https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/celery/celery.html with no luck in combination with running open-telemetry ... hat wobble

Activity

twiggy
added 
bug
Something isn't working
 on Mar 17, 2024
xrmx
xrmx commented on Mar 18, 2024
xrmx
on Mar 18, 2024
Contributor
Does this open-telemetry/opentelemetry-python-contrib#2342 looks relatable? If so any chance you can test the celery instrumentation from git https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation/opentelemetry-instrumentation-celery