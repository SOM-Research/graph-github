# graph-github
Democracy and dependencies of contributors in Open source Software development 

Ever wonder what a graph of the contributors in github would look like ? Here is the tool. It simply get all the commits of a given repository and exctracts the informations about the contributor, the number of commits and some other basic informations (login, mail, date of the commit, sha, etc...).

## how to make it run ?

First you need to install a few packages and libraries for the Python script to work.

```
pip install pygithub3
```

```
pip install plotly
```

```
pip install igraph
```

Then you just have to run the python script (contribution.py or comment.py) with some few arguments (what repository you want to work on) So juste type:

```
python graphGithub.py  <yourGithubUserName>  <userOfRepository>  <repository[/directory]>
```

for exemple:

```
python graphGithub.py AlexFabre twbs bootstrap/
```

A prompt will ask you for your github password to allow you making a the requests via the differents github API's.

This is [an example](http://www.alexfabre.com/include/project/twbs-bootstrap.html) of what it should display.  

## What do contain the json file ?

### contribution.py:




