def get_amazon_product_data(product = "laptop"):
    url , header  = f'https://www.amazon.in/laptop/s?k={product}', {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36(KHTML, like Gecko)Chrome/44.0.2403.157 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'}
    soup , data_frame  = BeautifulSoup(requests.get(url, headers=header).text, features='lxml'), DataFrame(columns=['Product Title', 'Product Link', 'Current Price of the product', 'Product Rating', 'MRP of the product', 'Discount'])
    for item, _ in zip_longest(
        soup.find_all(
            "div",
            attrs={"class": "s-result-item", "data-component-type": "s-search-result"},
        ),
        soup.find_all("div", attrs={"class": "a-row a-size-base a-color-base"}),
    ):
        try:
            product_title , product_link , product_price  = item.h2.text, 'https://www.amazon.in/' + item.h2.a['href'], item.find('span', attrs={'class': 'a-offscreen'}).text
            try:
                product_rating = item.find("span", attrs={"class": "a-icon-alt"}).text
            except AttributeError:
                product_rating = "Not available"
            try:
                product_mrp = (
                    "₹"
                    + item.find(
                        "span", attrs={"class": "a-price a-text-price"}
                    ).text.split("₹")[1]
                )
            except AttributeError:
                product_mrp = ""
            try:
                discount = float(
                    (
                        (
                            float(product_mrp.strip("₹").replace(",", ""))
                            - float(product_price.strip("₹").replace(",", ""))
                        )
                        / float(product_mrp.strip("₹").replace(",", ""))
                    )
                    * 100
                )
            except ValueError:
                discount = float("nan")
        except AttributeError:
            continue
        data_frame.loc[str(len(data_frame.index))] = [
            product_title,
            product_link,
            product_price,
            product_rating,
            product_mrp,
            discount,
        ]
    data_frame.loc[data_frame['Current Price of the product'] > data_frame['MRP of the product'], 'MRP of the product'] , data_frame.loc[data_frame['Current Price of the product'] > data_frame['MRP of the product'], 'Discount']  = ' ', ' '
    data_frame.index += 1
    return data_frame
