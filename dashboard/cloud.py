#!/usr/bin/env python
#
# This script is used to package a Titanium application in the cloud.
#

import sys, os, logging, time, urllib, urllib2, zipfile, StringIO

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise "Requires either simplejson or Python 2.6"


logger = logging.getLogger("titanium.cloud")

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logger.addHandler(NullHandler())


cloud_url = "https://api.appcelerator.net/p/v1/"

def login(app_path, user, password):

    url = cloud_url + "sso-login"    

    # get some app details
    h = open(os.path.join(app_path, "timanifest"))
    manifest = json.loads(h.read())
    h.close()

    logger.info("Logging in to %s", url)
    data = urllib.urlencode({"mid": manifest["mid"], "un": user, "pw": password})
    h = urllib2.urlopen(url, data)
    response = h.read()
    h.close()
    
    details = json.loads(response)
    
    if details["success"]:
        logger.info("Successfully logged in.")
    else:
        logger.warning("Login failed: %s", response)

    return details


def bundle(app_path, ignore=(".svn",)):

    def add_entry(path, archive):
        if os.path.isdir(path):
            for entry in [e for e in os.listdir(path) if e not in ignore]:
                entry = os.path.join(path, entry)
                add_entry(entry, archive)
        elif path not in ignore:
            archive.write(path, os.path.relpath(path, app_path))
        return
    
    entries = ("Resources", "modules", "timanifest", "manifest",
               "tiapp.xml", "CHANGELOG.txt", "LICENSE.txt")

    zip_data = StringIO.StringIO()
    archive = zipfile.ZipFile(zip_data, "w", zipfile.ZIP_DEFLATED)    
    for entry in entries:
        path = os.path.join(app_path, entry)
        logger.info("Bundling %s", path)
        if os.path.exists(path):
            add_entry(path, archive)
    archive.close()

    zip_data.seek(0)
    return zip_data


def package(zip_data, sid=None, token=None, uid=None, uidt=None):

    url = cloud_url + "publish"
    params = urllib.urlencode({
        "sid": sid,
        "token": token,
        "uid": uid,
        "uidt": uidt
    })
    data = zip_data.read()
    headers = {
        "Content-Type": "application/zip", 
        "Content-Length": str(len(data))
    }
    
    logger.info("Uploading app archive to %s", url)
    req = urllib2.Request("%s?%s" % (url, params), data, headers)
    h = urllib2.urlopen(req)
    response = h.read()
    h.close()
    
    details = json.loads(response)
    if details["success"]:
        logger.info("App archive accepted, package pending.")
    else:
        logger.warning("App archive rejected:\n%s", response)
    
    return details["ticket"]


def get_status(ticket):
    
    logger.info("Checking status for ticket %s", ticket)
    url = cloud_url + "publish-status"
    params = urllib.urlencode({"ticket": ticket})
    h = urllib2.urlopen("%s?%s" % (url, params))
    response = h.read()
    h.close()

    details = json.loads(response)
    return details


def wait(ticket, interval=30, timeout=300, start=None):

    if start is None:
        start = time.time()
    
    details = get_status(ticket)
    current = time.time()
    
    if details["status"] == "complete":
        logger.info("Packaging complete.")
        pass
    elif details.has_key("success"):
        if details["success"] == False:
            logger.warning("Packaging failed: %s", details["message"])
        else:
            logger.warning("Inconsistent response: %s", str(details))
        pass
    else:
        # keep waiting (get_status again later) unless timeout exceeded
        if current - start > timeout:
            logger.warning("Maximum wait time of %d seconds exceeded.  Giving up waiting on ticket %s.", timeout, ticket)
        else:
            logger.info("Packaging not yet complete.  Checking again in %d seconds.", interval)
            time.sleep(interval)
            details = wait(ticket, interval=interval, timeout=timeout, start=start)
    
    return details


def download(releases, dir=os.getcwd()):
    
    # only grab one per os (service occassionally returns two entries for same os)
    platforms = {}
    for entry in releases:
        platforms[entry["platform"]] = entry["url"]
    
    # download each
    for platform, url in platforms.items():
        logger.info("Downloading %s package %s", platform, url)
        h = urllib2.urlopen(url)
        data = h.read()
        meta = h.info()
        h.close()
        disp = meta.getheader("x-amz-meta-content-disposition")
        if disp is None:
            logger.warning("Trouble downloading %s package:\n%s", platform, data[:255])
        else:
            name = disp.split(";")[1].split("=")[1].replace('"', "")
            path = os.path.join(dir, name)
            logger.info("Saving %s", path)
            h = open(path, "wb")
            h.write(data)
            h.close()


def main():

    from optparse import OptionParser, OptionGroup

    # configure the command line parser
    parser = OptionParser(
        usage="usage: %prog [options] app_path",
        description="Build a Titanium app in the cloud."
    )
    parser.add_option(
        "-u", "--user",
        help="USER with permission to build the app (PASSWORD must be supplied as well)"
    )
    parser.add_option(
        "-p", "--password",
        help="PASSWORD for the USER"
    )
    parser.add_option(
        "-o", "--output",
        help="OUTPUT directory for saving downloaded packages"
    )
    parser.add_option(
        "-q", "--quiet",
        action="store_false", dest="verbose", default=True,
        help="don't print status messages"
    )
    
    group = OptionGroup(
        parser, "Non-login options", 
        "Provide these options if USER and PASSWORD are not supplied."
    )
    group.add_option("--sid")
    group.add_option("--token")
    group.add_option("--uid")
    group.add_option("--uidt")
    parser.add_option_group(group)

    (options, args) = parser.parse_args()
        
    if not len(args) == 1:
        parser.error("You must provide the path to your application.  Run with -h for help.")
    else:
        app_path = args[0]
    
    if not os.path.exists(app_path):
        parser.error("Can't find application %s." % (app_path,))

    # add handler for console to logger
    logger = logging.getLogger("titanium.cloud")
    console_handler = logging.StreamHandler()
    if options.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # gather app details
    details = {}
    if options.user and options.password:
        details = login(app_path, options.user, options.password)
    else:
        if not (options.sid and options.token and options.uid and options.uidt):
            parser.error("You must provide either USER and PASSWORD or all of SID, TOKEN, UID, and UIDT. Run with -h for help.")

        details["sid"] = options.sid
        details["token"] = options.token
        details["uid"] = options.uid
        details["uidt"] = options.uidt
    
    # bundle up app resources as a zip
    zip_data = bundle(app_path)
    
    # post app bundle for packaging (can't use **details here given unicode keys)
    ticket = package(zip_data, sid=details['sid'], token=details['token'], uid=details['uid'], uidt=details['uidt'])
    
    # keep checking status until complete
    job = wait(ticket)

    # download all releases
    output = options.output or os.getcwd()
    if not os.path.exists(output):
        os.makedirs(output)
    download(job["releases"], dir=output)


if __name__ == "__main__":
    main()
