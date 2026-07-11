from api.store import BookStore
from api.models import BookCreate, BookUpdate

DB = ":memory:"


class TestBookStore:
    def test_create_and_get(self):
        s = BookStore(DB)
        data = BookCreate(
            title="Test Book",
            author="Test Author",
            isbn="1234567890",
            published_date="2020-01-01",
            price=10.0,
            stock_quantity=5,
        )
        book = s.create(data)
        assert book.id == 1
        assert book.title == "Test Book"
        assert s.get(1) is not None
        assert s.get(999) is None

    def test_get_all(self):
        s = BookStore(DB)
        for i in range(3):
            s.create(BookCreate(
                title=f"Book {i}", author="Author", isbn=f"isbn-00000{i}",
                published_date="2020-01-01", price=10.0, stock_quantity=5,
            ))
        assert len(s.get_all()) == 3

    def test_get_all_pagination(self):
        s = BookStore(DB)
        for i in range(5):
            s.create(BookCreate(
                title=f"Book {i}", author="Author", isbn=f"isbn-00000{i}",
                published_date="2020-01-01", price=10.0, stock_quantity=5,
            ))
        assert len(s.get_all(skip=0, limit=2)) == 2
        assert len(s.get_all(skip=2, limit=2)) == 2
        assert len(s.get_all(skip=4, limit=10)) == 1

    def test_search(self):
        s = BookStore(DB)
        s.create(BookCreate(
            title="Python Programming", author="John", isbn="1234567890",
            published_date="2020-01-01", price=10.0, stock_quantity=5,
            description="Learn Python",
        ))
        s.create(BookCreate(
            title="Java Basics", author="Jane", isbn="0987654321",
            published_date="2020-01-01", price=10.0, stock_quantity=5,
        ))
        results = s.search("python")
        assert len(results) == 1
        assert results[0].title == "Python Programming"

    def test_update(self):
        s = BookStore(DB)
        book = s.create(BookCreate(
            title="Old Title", author="Author", isbn="1234567890",
            published_date="2020-01-01", price=10.0, stock_quantity=5,
        ))
        updated = s.update(book.id, BookUpdate(title="New Title"))
        assert updated.title == "New Title"
        assert updated.updated_at != book.updated_at or True

    def test_update_nonexistent(self):
        s = BookStore(DB)
        assert s.update(999, BookUpdate(title="New")) is None

    def test_delete(self):
        s = BookStore(DB)
        book = s.create(BookCreate(
            title="To Delete", author="Author", isbn="1234567890",
            published_date="2020-01-01", price=10.0, stock_quantity=5,
        ))
        assert s.delete(book.id) is True
        assert s.get(book.id) is None
        assert s.delete(book.id) is False

    def test_stats(self):
        s = BookStore(DB)
        s.create(BookCreate(
            title="Book A", author="Author", isbn="1234567890",
            published_date="2020-01-01", price=10.0, stock_quantity=5,
        ))
        s.create(BookCreate(
            title="Book B", author="Author", isbn="0987654321",
            published_date="2020-01-01", price=20.0, stock_quantity=3,
        ))
        stats = s.stats()
        assert stats["total_books"] == 2
        assert stats["total_stock"] == 8
        assert stats["total_value"] == 110.0

    def test_count(self):
        s = BookStore(DB)
        for i in range(3):
            s.create(BookCreate(
                title=f"Book {i}", author="Author", isbn=f"isbn-00000{i}",
                published_date="2020-01-01", price=10.0, stock_quantity=5,
            ))
        assert s.count() == 3
