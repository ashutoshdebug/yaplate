# 1. `decode`:
decode() method is used bytes object to convert it into a human-readable string object using a specified character encoding, such as utf-8
```python
bytes_object.decode(encoding="utf-8", errors="strict")
```
### Example
```python
# A bytes object (note the 'b' prefix)
encoded_bytes = b'Hello, world!'

# Decode using UTF-8 encoding
decoded_string = encoded_bytes.decode('utf-8')

print(decoded_string)
# Output: Hello, world!

```

---

# 2. `bytes`:
It is an immutable sequence of single bytes, used to store raw binary data

---

# 3. `isinstance`: 
isinstance helps to verify whether any value or variable whether is a part of class/subclass or not
isinstance(object, classinfo)
### Example:
```python
a = 5
print(isinstance(a, int)) # returns True because a is int
```
OR
```python
value = "hello"
### Check if value is an instance of str or tuple
if isinstance(value, (str, tuple)):
    print("Is a string or a tuple")
else:
    print("Is neither a string nor a tuple")
### Output: Is a string or a tuple
```

---

# 4. `set`:
set() is a Redis method used to store a value for a key in the Redis database.

### Example
```python
r.set("fullname", "John Doe")
True
```

---

# 5. `delete`:
Delete the given key in the cluster. The keys are first split up into slots and then an DEL command is sent for every slot
```python
r.delete("my_key")
```

---

# 6. `exists`:
It is a method that checks whether one or more specified keys exist in the Redis database
```python
r.set("key1", "Hello")
if r.exists("key1"):
    print("key1 exists")
```

---

# 7. `get`:
It is a method that fetches a value of any key in the Redis Database
```python
r.set("full_name", "override")
r.get("full_name")
# Output: override
```

---

# 8. `scan_iter`:

`scan_iter()` is a Redis method that **iterates over keys lazily** (in small batches) instead of fetching all keys at once like `keys("*")`.

It is useful when the database has many keys because it is **more memory-efficient and safer** than `keys()`.

```python
r.scan_iter(match=None, count=None)
```

### Example

```python
# Suppose Redis has keys: user:1, user:2, product:1

for key in r.scan_iter(match="user:*"):
    print(key.decode("utf-8"))
```

### Output

```python
user:1
user:2
```

---

# 9. `hset`:

`hset()` is used to **set field-value pairs inside a Redis hash**.

A hash in Redis is like a Python dictionary where one key stores multiple fields and values.

```python
r.hset(name, key, value)
```

OR for multiple fields:

```python
r.hset(name, mapping={"field1": "value1", "field2": "value2"})
```

### Example

```python
r.hset("user:1", "name", "Ashutosh")
r.hset("user:1", "age", 20)
```

OR

```python
r.hset("user:1", mapping={"name": "Ashutosh", "age": 20})
```

---

# 10. `hgetall`:

`hgetall()` is used to **retrieve all fields and values of a Redis hash**.

It returns the data in the form of a dictionary (usually as bytes if `decode_responses=False`).

```python
r.hgetall(name)
```

### Example

```python
r.hset("user:1", mapping={"name": "Ashutosh", "age": "20"})
data = r.hgetall("user:1")

print(data)
```

### Output

```python
{b'name': b'Ashutosh', b'age': b'20'}
```

If `decode_responses=True` is enabled:

```python
{'name': 'Ashutosh', 'age': '20'}
```

---

# 11. `zadd`:

`zadd()` is used to **add one or more members with scores to a sorted set in Redis**.

A sorted set stores unique members, each associated with a numeric score, and Redis keeps them ordered by score.

```python
r.zadd(name, mapping)
```

### Example

```python
r.zadd("leaderboard", {"Ashutosh": 100, "Rahul": 200, "Aman": 150})
```

Here:

* `"leaderboard"` = sorted set name
* `"Ashutosh"`, `"Rahul"`, `"Aman"` = members
* `100`, `200`, `150` = scores

---

# 12. `zrem`:

`zrem()` is used to **remove one or more members from a sorted set**.

```python
r.zrem(name, *values)
```

### Example

```python
r.zadd("leaderboard", {"Ashutosh": 100, "Rahul": 200})
r.zrem("leaderboard", "Ashutosh")
```

This removes `"Ashutosh"` from the sorted set `"leaderboard"`.

---

# 13. `zrange`:

`zrange()` is used to **get members from a sorted set within a given index range**.

By default, results are returned in **ascending order of score**.

```python
r.zrange(name, start, end, withscores=False)
```

### Example

```python
r.zadd("leaderboard", {"Ashutosh": 100, "Rahul": 200, "Aman": 150})

print(r.zrange("leaderboard", 0, -1))
```

### Output

```python
[b'Ashutosh', b'Aman', b'Rahul']
```

With scores:

```python
print(r.zrange("leaderboard", 0, -1, withscores=True))
```

### Output

```python
[(b'Ashutosh', 100.0), (b'Aman', 150.0), (b'Rahul', 200.0)]
```

---

# 14. `zrangebyscore`:

`zrangebyscore()` is used to **get members from a sorted set whose scores fall within a specific range**.

```python
r.zrangebyscore(name, min, max, withscores=False)
```

### Example

```python
r.zadd("leaderboard", {"Ashutosh": 100, "Rahul": 200, "Aman": 150})

print(r.zrangebyscore("leaderboard", 100, 160))
```

### Output

```python
[b'Ashutosh', b'Aman']
```

With scores:

```python
print(r.zrangebyscore("leaderboard", 100, 160, withscores=True))
```

### Output

```python
[(b'Ashutosh', 100.0), (b'Aman', 150.0)]
```

---

# 15. `zscore`:

`zscore()` is used to **get the score of a specific member in a sorted set**.

```python
r.zscore(name, value)
```

### Example

```python
r.zadd("leaderboard", {"Ashutosh": 100, "Rahul": 200})

print(r.zscore("leaderboard", "Rahul"))
```

### Output

```python
200.0
```

---

# 16. `rename`:

`rename()` is used to **change the name of an existing Redis key**.

It renames an old key to a new key.

```python
r.rename(src, dst)
```

### Example

```python
r.set("old_key", "Hello Redis")
r.rename("old_key", "new_key")

print(r.get("new_key"))
```

### Output

```python
b'Hello Redis'
```

---


