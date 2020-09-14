## Testing

``` bash
source path-to-env/bin/activate

# type checking
mypy .

# unit tests
python -m unittest discover -s tests

# formatting
black --check .
black .
```
