# load the contents of .env into environment variables
# override by calling `just --dotenv-filename ENV_FILENAME COMMAND`
# where ENV_FILENAME is the file containing env vars you want to use instead
set dotenv-load

# list all the available commands
default:
  just --list

# run a command with uv, but with environment variables loaded from a dotenv file
run *options:
  uv run {{ options }}

# run the tests, with the ability to pass in options
test *options:
  uv run pytest {{ options }}

# clear the dist directory, and build the project, ready for publishing
build:
  rm -rf ./dist
  uv build
