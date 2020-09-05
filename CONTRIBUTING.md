## Testing

``` bash
source path-to-env/bin/activate

# type checking
mypy icongen svg2png

# unit tests
python -m unittest discover -s tests

# actual convertion test
python test_convert.py

# formatting
black --check .
black .
```
