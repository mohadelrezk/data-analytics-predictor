import urllib2
import urllib




def URLRequest(url, params, method="GET"):
    if method == "POST":
        request =  urllib2.Request(url, data=urllib.urlencode(params))
        response = urllib2.urlopen(request)
        return response.read()
    else:
        print "http request - final url: " , url + "?" + urllib.urlencode(params)
        request=  urllib2.Request(url + "?" + urllib.urlencode(params))
        response= urllib2.urlopen(request)
        return response.read()


url_git_repo = "https://api.github.com/search/repositories"
post_fields = {'q': 'rapidminer', 'sort':'starts','order':'desc'}     # Set POST fields here
response= URLRequest(url_git_repo,post_fields,"POST")

"""
print "request.type: " , request.type
print "request.data: " , request.data
print "request.origin_req_host: " , request.origin_req_host
print "request.port: " , request.port
print "request.headers: " , request.headers
print "request.host: " , request.host
"""

print response
