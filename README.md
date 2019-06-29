# PyHP-Interpreter

This repository includes a script that allows you to embed Python code like PHP code into HTML.
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
 - if "-c" is given, the file will be processed an cached in /etc/pyhp/relative/to/document root/filename.cache
   (the file is also loaded or renewed with this option)
 - python code can be away from the left site of the file for better optics --> Test4.pyhp
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
  - `setrawcookie`
  - `setcookie`
  - automatic sending of headers with fallback: `Content-Type: text/html`
  
  ## Installation
  1. enable CGI for your web server
  2. drop pyhp.py somewhere and mark it as executable (make sure Python 3.4+ is installed)
  3. to enable the support for caching, create the directory `/etc/pyhp` and give the Webserver permission to read/write
  4. Done! you can now use `.pyhp` files by adding a Shebang
