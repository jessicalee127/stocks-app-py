from robo_adviser import write_prices_to_file
# so by invoking this function, we are ensuring the default file exists
# ... so when we run the application, it will be able to write to this file
write_prices_to_file(prices=[], filename="db/prices.csv")
