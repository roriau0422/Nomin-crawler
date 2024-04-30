class Product:
    def __init__(self, sku, mpn, description, image_url, brand, name, alternate_name, price):
        self.sku = sku
        self.mpn = mpn
        self.description = description
        self.image_url = image_url
        self.brand = brand
        self.name = name
        self.alternate_name = alternate_name
        self.price = price

    def to_dict(self):
        return {
            'sku': self.sku,
            'mpn': self.mpn,
            'description': self.description,
            'image_url': self.image_url,
            'brand': self.brand,
            'name': self.name,
            'alternate_name': self.alternate_name,
            'price': self.price
        }