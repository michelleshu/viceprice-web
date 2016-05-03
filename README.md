## Code Structure:

* `env/`: files that contain environment variables (database URL, API keys), only production on Git
  * Michelle to add logic to use development DB if environment variable not defined

* `viceprice/`: project directory
  * `constants.py` - any constant value
  * `settings.py` - standard Django settings
  * `urls.py` - routing logic

* `vp/` - application directory
  * `management` - `python manage.py *`
    * Define one-off commands to interact with code or data
    * Define scheduled processes for server (use clock.py and worker.py)
  * `migrations`
    * Added by `python manage.py makemigrations`
    * Run by `python manage.py migrate`
    * Only edit `models.py` and run migrations to add/remove/edit columns and tables, do not edit database directly
  * `mturk` - Contains code that evaluates MTurk HITS
  * `static` - All CSS/JS/image files
    * Preprocess static files before running server with `python manage.py collectstatic`
  * `templates` - HTML templates (reference [Django doc](https://docs.djangoproject.com/en/1.9/topics/templates/) for syntax)
  * `models` - Data models
  * `tests` - Unit tests
    * Run on local DB (set up SQLite)
    * Write for back end logic, no front end tests for now
  * `views`
    * Contains all HTTP endpoints
    * Links the templates to URLs
    * Add corresponding line in `urls.py`


## Data Model
(`models.py`)

### Location
* Name, address, phone number, etc

### Deals
* Deal details
* Active hours

### DealDetail
* Type (price, % off, price off)
* Value (e.g. 5)
* Drink category (beer, wine, liquor)
* Item names

### ActiveHours
* Day of the week
* Start time
* End time (if null end time is “until_close”)



## Code Reviews

### Feature Branching
* For each Trello item you work on, create a new branch off of master
* `git checkout -b`
* Push to remote branch with the same name
* [github.com](https://github.com/VicePrice/viceprice-web.git) ->  Create pull request
* Default reviewers:

### What does it mean to review?
* Quick read through code on GitHub
* Check out the branch, run server locally
* Add comments to Pull Request

### If there is review feedback:
* Fix errors/add enhancements on same branch you wrote code in
* GitHub automatically updates pull request

### All good -
* (Click `Merge Pull Request`) Merge the branch into `master` and delete original branch
