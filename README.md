# PyHP-Interpreter  [![Build Status](https://travis-ci.org/Deric-W/PyHP-Interpreter.svg?branch=master)](https://travis-ci.org/Deric-W/PyHP-Interpreter)

The PyHP Interpreter is a script that allows you to embed Python code like PHP code into HTML.
The script is called either by the configuration of the web server or a shebang and communicates with the web server via CGI.

## Features:
  - Parser for embedding python Code in HTML
  - Encapsulation of the variables and functions of the interpreter in a separate class (to prevent accidental overwriting)
  - caching
  - PHP like header functions
  - PHP like SERVER array (Dictionary)
  - PHP like REQUEST,GET,POST and COOKIE array (Dictionary)
  - PHP like setrawcookie and setcookie functions
  
## How it works:
 - Python code is contained within the `<?pyhp` and `?>` tags (like PHP)
 - the Script is called like a interpreter, with the filepath as cli parameter
 - if no filepath is given, the script is reading from stdin
 - if "-c" is given, the file will be processed an cached in cache_path/absolute/path/filename.cache
   (the file is also loaded or renewed with this option)
 - python code can be away from the left site of the file for better optics --> Test4.pyhp, fib.pyhp
 - the following PHP features are available as part of the `pyhp` class:
  - `$_REQUEST` as REQUEST
  - `$_GET`as GET
  - `$_POST`as POST
  - `$_COOKIE`as COOKIE
  - `$_SERVER` as SERVER
  - `http_response_code`
  - `headers_list`
  - `header`
  - `header_remove`
  - `headers_sent`
  - `header_register_callback`
  - `setrawcookie`
  - `setcookie`
  - `register_shutdown_function`
 - automatic sending of headers with fallback: `Content-Type: text/html`
  
  ## Cache Handlers
   - are responsible for saving/loading/renewing caches
   - are python scripts with the following contents:
   - the `handler` class, wich takes the cache path, absolute file path and the 'caching' config as initialization parameters
   - the method `is_available`, wich returns True or False depending on the ability of the handler to cache
   - the method `is_outdated`, wich returns True or False depending on the the timeliness of the cache entry
   - the method `save`, wich returns nothing and saves the boolean code_at_begin and preprocessed code
   - the method `load`, wich returns a tuble with the boolean code_at_begin and the code saved by `save`
   - the method `close`, wich does cleanup tasks
  
  ## Installation
  ### Debian
  Use the Debian package
  ### Other
  1. enable CGI for your web server
  2. drop pyhp.py somewhere and mark it as executable (make sure Python 3.5+ is installed)
  3. download pyhp.conf and move it to `/etc`
  4. create `/lib/pyhp/cache_handlers` and drop the choosen cache handler (and maybe others) in the cache handler directory
  
  Done! you can now use `.pyhp` files by adding a Shebang
