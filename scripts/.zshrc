source /root/antigen.zsh

# Load the oh-my-zsh's library.
antigen use oh-my-zsh

antigen theme robbyrussell

antigen bundle zsh-users/zsh-syntax-highlighting

# Tell antigen that you're done.
antigen apply

alias pm="python manage.py"
alias cdapp="/usr/src/app"
alias pmrun="python manage.py runserver 0.0.0.0:8000 --settings=bender_service.settings.development"
