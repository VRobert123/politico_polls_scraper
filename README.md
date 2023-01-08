# Download polls from Politico Polls with this Python package.
 Politico collects polls data from all european country, but doesn't give a possibility to download this data. If you want to use these polls data you can easy download that with this package in python. It's just some seconds. 

There are some countries what is not available in the package, please consider upgrades in the future.

This package uses Python Selenium with Chrome driver. After the scraping of x and y axis, the package scraps every points's position, then with a simple linear regression, turn cx and cy values to dates and percentages. 

Let me know if you have any observation.

# Usage

Import the package:

```
from politicopolls import politico
```


Assign a variable with the class in the module.
```
var = politico.Politico()
```

To get a list about available countries, type this:
```
var.get_list()
```

To download polls from a country, use this:
```
var.download('hungary')
```

If you want to work with the result dataframe, you can do this:

```
var.df
```

# Please notice

This is my first Python package, you can expect bugfixes and upgrades. The package uses Selenium and pandas so maybe a little bit slow. I am on it.

# License

MIT License
