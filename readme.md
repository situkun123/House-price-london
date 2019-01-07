# House-price-london

_A project for exploring london house prices in 2018_ <br>
_The inspriation is coming from my needs to buy a house_ <br>

![](https://github.com/situkun123/House-price-london/blob/master/img/3-reasons-why-london-house-prices-are-falling.jpg)

## Part1

- Filter through the data from the UK house dataset.
- Obtain some insightful information from the filtered dataset.
- Use GeoPandas to plot a London heatmap with different borourgh's average flat prices

## Part2
- Explore further with the London house price 2018 dataset.
- Process the dataset to generate more insights (e.g. smoothing, secondary data calculation, etc.)
- Use fbprophet to do some seasonality analysis, and trying to predict the average London flat price for the rest of 2018

## Brand new approach
- Use Zoopla to scrape housing data
- An simple API was built
- All files are in package directory
- There are jupyter notebook demonstrations to illustrate how these package can be used.

## Covered areas
```python
district_postcode = [
    ('Hackney', 'E8'), ('E-head', 'E1'), ('Bethal green', 'E2'), ('EC-head', 'EC1'), 
    ('Bishopsgate', 'EC2'),('French chruch street', 'EC3'), ('Fleet strett', 'EC4'), 
    ('N-head', 'N1'),  ('Highbury', 'N5'), ('Highgate', 'N6'), ('Finsbury park', 'N4'),
     ('NW-head', 'NW1'),('Cricklewood', 'NW2'), ('Hampstead', 'NW3'), ('Kentish town', 'NW5'),
       ('Kilburn', 'NW6'), ('St John wood', 'NW8'),('SE-Head', 'SE1'),
      ('Greenwich', 'SE10'), ('SW-Head', 'SW1'), ('Chelsea', 'SW3'),
       ('Clapham', 'SW4'), ('Earls court', 'SW5'),('Fulham', 'SW6'),
       ('South kensington', 'SW7'), ('South lambeth', 'SW8'), ('Stockwell', 'SW9'),
        ('West Brompton', 'SW10'), ('SW-head', 'SW11'), ('Paddington','W2'),
      ('North Kensington', 'W10'), ('Notting hill', 'W11'), ('West Kensington', 'W14'),
       ('WC-head', 'WC1'), ('Strand', 'WC2')
      ]
```
## GUI for visualisation (In development)
### Overview
![](https://github.com/situkun123/House-price-london/blob/master/img/GUI_overview.png)

### All listed price in NW5 (Kentish Town) against listed time 
- 14-day moving average smoothing
![](https://github.com/situkun123/House-price-london/blob/master/img/GUI_all_listPrice.png)

### Average property price in different London region on a listed date
![](https://github.com/situkun123/House-price-london/blob/master/img/GUI_daily_stats.png)

### Cumulative average price of NW5 (Kentish Town) against listed time 
- 4 day of moving average smoothing
![](https://github.com/situkun123/House-price-london/blob/master/img/GUI_Cul_list_price.png)
