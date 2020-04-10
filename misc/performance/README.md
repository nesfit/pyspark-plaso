# Performace Evaulation


## Original Plaso

~~~sh
docker run -ti registry.gitlab.com/rychly-edu/docker/docker-plaso:latest
~~~

~~~ sh
apt update
apt install plaso-tools wget zip

wget .../plaso-test_data-20200227.zip
unzip plaso-test_data-20200227.zip
~~~

~~~sh
time log2timeline.py --parsers "pe,$(log2timeline.py --parsers list | grep -o 'sqlite/[^ ]*' | tr '\n' ',')" results.plaso test_data
# main events 3002
# real	0m13.375s

time psort.py -o json -w results.json results.plaso
# events 10836
# real	0m4.440s
~~~

OR

~~~sh
time ( rm results.*; log2timeline.py --parsers "pe,$(log2timeline.py --parsers list | grep -o 'sqlite/[^ ]*' | tr '\n' ',')" results.plaso test_data; psort.py -o json -w results.json results.plaso )
# real	0m15.504s
~~~

### Results

~~~sh
grep '"filename"' results.json | sort | uniq -c
~~~

~~~
      5     "filename": "/test_data/application_usage.sqlite",
      5     "filename": "/test_data/contacts2.db",
   1755     "filename": "/test_data/cookies.db",
     16     "filename": "/test_data/Cookies-68.0.3440.106",
      4     "filename": "/test_data/document_versions.sql",
      2     "filename": "/test_data/downloads.sqlite",
    295     "filename": "/test_data/firefox_cookies.sqlite",
     71     "filename": "/test_data/History",
      2     "filename": "/test_data/History-57.0.2987.133",
      2     "filename": "/test_data/History-58.0.3029.96",
      2     "filename": "/test_data/History-59_added-fake-column",
      2     "filename": "/test_data/History-59.0.3071.86",
     10     "filename": "/test_data/imessage_chat.db",
    198     "filename": "/test_data/mackeeper_cache.db",
     51     "filename": "/test_data/mac_knowledgec-10.13.db",
    229     "filename": "/test_data/mac_knowledgec-10.14.db",
      9     "filename": "/test_data/mmssms.db",
      6     "filename": "/test_data/NotesV7.storedata",
     84     "filename": "/test_data/places_new.sqlite",
    202     "filename": "/test_data/places.sqlite",
     24     "filename": "/test_data/skype_main.db",
      1     "filename": "/test_data/test_driver.sys",
      3     "filename": "/test_data/test_pe.exe",
      4     "filename": "/test_data/Web Data",
     10     "filename": "/test_data/webviewCache.db",
      8     "filename": "/test_data/webview.db",
~~~


## PySpark Plaso

~~~sh
time ./client-extract.sh | grep -c hdfs
# events 4185
# real	0m9.007s
~~~

### Results

~~~sh
grep hdfs plaso-test_data-20200227-extracted_events.json | sort | uniq -c
~~~

~~~
     44   "hdfs://hadoop@namenode:8020/test_data/test_data/activity.sqlite",
      5   "hdfs://hadoop@namenode:8020/test_data/test_data/application_usage.sqlite",
      5   "hdfs://hadoop@namenode:8020/test_data/test_data/contacts2.db",
   1755   "hdfs://hadoop@namenode:8020/test_data/test_data/cookies.db",
      2   "hdfs://hadoop@namenode:8020/test_data/test_data/downloads.sqlite",
    295   "hdfs://hadoop@namenode:8020/test_data/test_data/firefox_cookies.sqlite",
     14   "hdfs://hadoop@namenode:8020/test_data/test_data/googlehangouts.db",
     71   "hdfs://hadoop@namenode:8020/test_data/test_data/History",
     25   "hdfs://hadoop@namenode:8020/test_data/test_data/History.db",
      2   "hdfs://hadoop@namenode:8020/test_data/test_data/History-57.0.2987.133",
      2   "hdfs://hadoop@namenode:8020/test_data/test_data/History-58.0.3029.96",
      2   "hdfs://hadoop@namenode:8020/test_data/test_data/History-59_added-fake-column",
      2   "hdfs://hadoop@namenode:8020/test_data/test_data/History-59.0.3071.86",
     10   "hdfs://hadoop@namenode:8020/test_data/test_data/imessage_chat.db",
     60   "hdfs://hadoop@namenode:8020/test_data/test_data/kik_ios.sqlite",
    198   "hdfs://hadoop@namenode:8020/test_data/test_data/mackeeper_cache.db",
      9   "hdfs://hadoop@namenode:8020/test_data/test_data/mmssms.db",
      4   "hdfs://hadoop@namenode:8020/test_data/test_data/MyVideos107.db",
     84   "hdfs://hadoop@namenode:8020/test_data/test_data/places_new.sqlite",
    202   "hdfs://hadoop@namenode:8020/test_data/test_data/places.sqlite",
     14   "hdfs://hadoop@namenode:8020/test_data/test_data/quarantine.db",
     24   "hdfs://hadoop@namenode:8020/test_data/test_data/skype_main.db",
     30   "hdfs://hadoop@namenode:8020/test_data/test_data/snapshot.db",
    115   "hdfs://hadoop@namenode:8020/test_data/test_data/tango_android_profile.db",
     43   "hdfs://hadoop@namenode:8020/test_data/test_data/tango_android_tc.db",
      1   "hdfs://hadoop@namenode:8020/test_data/test_data/test_driver.sys",
      3   "hdfs://hadoop@namenode:8020/test_data/test_data/test_pe.exe",
    850   "hdfs://hadoop@namenode:8020/test_data/test_data/twitter_android.db",
    184   "hdfs://hadoop@namenode:8020/test_data/test_data/twitter_ios.db",
     10   "hdfs://hadoop@namenode:8020/test_data/test_data/webviewCache.db",
      8   "hdfs://hadoop@namenode:8020/test_data/test_data/webview.db",
    112   "hdfs://hadoop@namenode:8020/test_data/test_data/windows_timeline_ActivitiesCache.db",
~~~
