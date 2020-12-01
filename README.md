# unix-history-backend

## Know issues
### `Site matching query does not exist.`
если ругается `Site matching query does not exist.`

запустите `./manage.py shell`

и вбейте туда
`from django.contrib.sites.models import Site
new_site = Site.objects.create(domain='unix-history.org', name='unix-history.org')
print (new_site.id)`