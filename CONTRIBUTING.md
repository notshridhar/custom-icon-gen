## Testing

``` bash
source path-to-env/bin/activate

mypy icongen svg2png
python -m unittest discover -s tests
python test_convert.py
```
