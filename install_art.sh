#!/bin/bash
NC='\033[0m' # No Color
BRED='\033[1;31m'
GREEN='\033[0;32m'
WHITE='\033[0;37m'
BWHITE='\033[1;37m'
BCYAN='\033[1;36m'

install_system_dependencies()
{
    #homebrew
    count=0
    echo -e "${BWHITE}Checking HomeBrew"
    while ! [ "$(command -v brew)" ] && [ $count -lt 3 ]; do
        echo -e "${BWHITE}Installing HomeBrew"
        /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
        count=$((count + 1))
    done
    if ! [ "$(command -v brew)" ]; then
        echo -e "${BRED}Unable to install HomeBrew"
        return
    fi
    # python
    echo -e "${BWHITE}Checking Python version"
    py_version=$(python --version)
    echo -e "${GREEN}$py_version"
    required_version="Python 3"
    if [[ $py_version != "$required_version"* ]] || ! [[ $(command which python3) ]]; then
        echo -e "${BCYAN}Python 3 required. Continue with installation? (Y/n)"
        read -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            brew install python
        else
            return
        fi
    fi
    # pipenv
    touch .env
    echo -e "${BWHITE}Checking pipenv"
    if ! [ "$(command -v pipenv)" ]; then
        echo -e "${BWHITE}Installing pipenv"
        brew install pipenv
    fi
    echo -e "${WHITE}Checking .env file for database env var"
    while IFS='' read -r line || [[ -n "$line" ]]; do
        if [[ $line = *"DATABASE_URL"* ]]; then
            db_url="$line"
        else
            echo -E "$line" >> .env.tmp
        fi
    done < .env
    mv .env{.tmp,}
    if [ -n "$db_url" ]; then
        echo -e "
        ${BCYAN}You have an existing DATABASE_URL variable in your .env file.
        \t$db_url
        Would you like to keep it?
        "
        read -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -E "$db_url" >> .env
            echo -e "If you choose to set up the db this file will be overwritten."
        fi
    fi
    # shell-check
    count=0
    echo -e "${BWHITE}Checking shellcheck"
    while ! [ "$(command -v shellcheck)" ] && [ $count -lt 3 ]; do
        echo -e "${BWHITE}Installing shellcheck"
        brew install shellcheck
        count=$((count + 1))
    done
    if ! [ "$(command -v shellcheck)" ]; then
        echo -e "${BRED}Unable to install shellcheck"
        return
    fi

    # database
    echo -e "${BCYAN}Would you like to set up the database? (Y/n)"
    read -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_postgres
    else
        echo -e "${BWHITE}Please add the database url to your .env file in the format:"
        echo -e "${BCYAN}\t DATABASE_URL=postgresql://<user>:<password>@localhost:5432/<db>"
    fi
}

setup_postgres()
{
    echo -e "${BWHITE}Checking PostgreSQL"
    count=0
    while ! [ "$(command -v psql)" ] && [ $count -lt 3 ]; do
        echo -e "${BCYAN}PostgreSQL not found. Installing"
        brew install postgresql
        count=$((count + 1))
    done
    if ! [ "$(command -v psql)" ]; then
        echo -e "${BRED}Unable to install PostgreSQL"
        return
    fi
    echo -e "${BWHITE}Checking for existing postgres role"
    postgres_role=$(psql postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='postgres'")

    if [[ $postgres_role =~ 1 ]]; then
        create_app_database "postgres"
    else
        echo -e "${BCYAN}'postgres' user role not found. Would you like to use an existing user? (Y/n)"
        read -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            count=0
            echo -e "${BWHITE}Please enter the username of an admin user"
            read -r
            while [ "$REPLY" = "" ] && [ $count -lt 3 ]; do
                count=$((count + 1))
                echo -e "${BWHITE}Please enter the username of an admin user"
                read -r
            done
            if [[ $REPLY != "" ]]; then
                create_app_database "$REPLY"
            else
                echo -e "${BCYAN}Please create the database manually and update the .env file"
            fi
        else
            echo -e "${BCYAN}Please create the database manually and update the .env file"
            return
        fi
    fi
}
create_app_database()
{
    postgres_role=$(psql postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$1'")
    if [[ $postgres_role =~ 1 ]]; then
        echo -e "${BCYAN}Using role: '$1'"
        echo -e "${BCYAN}Creating database art_db"
        success=true
        user_db=$(psql postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$1'")
        if [[ $user_db != 1 ]]; then
            createdb "$1"
        fi
        if [[ $postgres_role != 1 ]]; then
            db_output=$(createdb art_db)
            if [ "$db_output" != 0 ]; then
                success=false
            fi
        fi
        echo -e "${BCYAN}Creating user art_db with password art_db"
        app_user_role=$(psql postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='art_db'")
        if [[ $app_user_role =~ 1 ]]; then
            echo -e "${BCYAN}User art_db already exists"
        else
            create_role_output=$(psql --command "CREATE ROLE art_db WITH PASSWORD 'art_db' LOGIN;" -U "$1")
            if [ "$create_role_output" != 0 ]; then
                success=false
            else
                echo -e "${BCYAN}Updating art_db privileges"
                psql --command "ALTER USER art_db with SUPERUSER;"
            fi
        fi
        if [ $success = false ]; then
            echo -e "${BCYAN}Error. Please create the database manually and update the .env file"
        else
            echo -e "${GREEN}Database successfully created."
            echo -e "\nDATABASE_URL=postgresql://art_db:art_db@localhost:5432/art_db" >> .env
        fi
    else
        echo -e "${BCYAN}User not found. Please create the database manually and update the .env file"
        return
    fi
}

prep_application()
{
    pipenv install --dev
    echo -e "${WHITE}Checking .env file for database env var"
    db_url_env_exists=false
    while IFS='' read -r line || [[ -n "$line" ]]; do
        if [[ $line = *"DATABASE_URL"* ]]; then
            db_url_env_exists=true
        fi
    done < .env
    if [[ $db_url_env_exists = true ]]; then
        migration_command=$(pipenv run python manage.py migrate)
        if [ "$migration_command" != 0 ]; then
            echo -e "${BRED}Error running migrations."
        fi
    else
        echo -e "${BRED}Env variable DATABASE_URL not found. Please update the .env file and run 'python manage.py migrate'"
    fi
    echo -e "
    ${GREEN}Setup complete. Please check the console output for any errors.
    ${NC}Make sure you update the .env file before starting the application.
    ${NC}You may also need to run the command 'python manage.py createsuperuser' to create a superuser account.
    ${NC}Please check the README for more details.
    ${BCYAN}Done"
    pipenv shell
}

main()
{
    echo -e "
    This script will install the following if they don't exist:
    \tHomeBrew
    \tPython 3
    \tPipenv
    \tdependencies
    \tShellCheck
    \tPostgreSQL
    It will also:
    \tCreate a .env file
    \tCreate a user 'art_db' and postgres db 'art_db'
    \tDelete DATABASE_URL from .env. If you choose not to setup the db please add the var back to .env
    \tOtherwise 'DATABASE_URL=postgresql://art_db:art_db@localhost:5432/art_db' will be added to .env
    Continue? (Y/n)
    "
    read -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_system_dependencies
        prep_application
    fi
}

main "$@"
