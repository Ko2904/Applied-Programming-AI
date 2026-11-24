import unittest

from scraper import parse_listing


class ParseListingTests(unittest.TestCase):
    def test_extracts_book_fields_and_resolves_relative_urls(self):
        html = """
        <article class="product_pod">
          <p class="star-rating Three"></p>
          <h3><a href="example-book_1/index.html" title="Example Book">Example...</a></h3>
          <div class="product_price">
            <p class="price_color">£12.34</p>
            <p class="availability"> In stock (2 available) </p>
          </div>
          <div class="image_container"><img src="../media/book.jpg" /></div>
        </article>
        """
        books = parse_listing(html, "https://books.toscrape.com/catalogue/page-2.html")

        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].title, "Example Book")
        self.assertEqual(books[0].price, 12.34)
        self.assertEqual(books[0].rating, 3)
        self.assertEqual(books[0].availability, "In stock (2 available)")
        self.assertEqual(
            books[0].source_url,
            "https://books.toscrape.com/catalogue/example-book_1/index.html",
        )
        self.assertEqual(books[0].image_url, "https://books.toscrape.com/media/book.jpg")

    def test_rejects_incomplete_listing(self):
        with self.assertRaisesRegex(ValueError, "Incomplete book listing"):
            parse_listing('<article class="product_pod"></article>', "https://example.test/")


if __name__ == "__main__":
    unittest.main()
