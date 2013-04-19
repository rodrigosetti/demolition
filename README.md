# Demolition

Demolition is a web application written in python using the excellent Django
Framework.

It is an event planner and manager in which administrators can register new
events and allow users to participate in order to control number of
participants, companions, elaborate charge and confirm best dates.

The project is still in its beginning as it needs more features to get fully
usable for real world stuff. Meantime I'm using it for personal event and
parties i gave to my friends and it proves to be a very useful tool in such
cases.

Anyway, if you're a developer you're welcome to clone and write new features,
fix bugs, change stuff. I'll be glad to merge any contributions.

Right now I'm looking forward to build the following features:

 * Automating mailing to confirm acceptance of participations
 * Automating mailing to inform about confirmed events and other state changes
 * Some protection at sign up like captcha or email confirmation
 * Translations to any language you can help 

## Installation

To install the system follow the procedure to install any other Django project:

 1. Create a new file called local_settings.py which will be imported by
    settings.py . There you can set local configurations like database
    connection, language, path and url stuff (please refer to django
    documentation)

 2. Run: python manage.py syncapp in order to create the database tables.

 3. Run: python manage.py compilemessages in order to create the localization
    file (currently, portuguese only) 

