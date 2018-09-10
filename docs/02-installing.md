Installing Sparrow for development
============================================

This project uses docker and docker-compose. The `docker-compose.yml`
uses the file format version `3.2`, so make sure to use a version of
docker-compose that supports it.

First off, copy `example.env` to a local, git-ignored `.env`, then
open it and edit its variables as you see fit. If you intend to follow
this chapter and run the project within a container, then you'll only
need to concern with `SPARROW_DATA_DIR`. It points to a directory
that'll persist some data, namely the database and the Python
dependencies installed within the container. it defaults to `/tmp/`
but you might want to choose a more persistent folder.

Then, there's a `Makefile` with a few shortcuts. For setting up the
images and install all dependencies, run `make build`. This command
will:
- build a Python image to run sparrow
- install the Python dependencies inside of it, both for running and
  testing

After that's been done sparrow is now ready to be run, so you can move
to the next chapter.
