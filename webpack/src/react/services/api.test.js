import {
  searchUrl,
  queryString,
  httpOptions,
  paramPairs,
  cleanValues,
  isEmpty,
} from './api'

test('object to url query parameters', () => {
  expect(
    queryString({
      names_in: [],
      search: 'hello world!',
      limit: 20,
    })
  ).toBe('search=hello%20world!&limit=20')

  expect(
    queryString({
      data_in: [1, 7, 3, 4],
      foo: null,
      search: '',
      name: 'Håken',
    })
  ).toBe('data_in=1,7,3,4&name=H%C3%A5ken')
})

test('isEmpty', () => {
  R.map(value => expect(isEmpty(value)).toBe(true), [
    [],
    {},
    '',
    null,
    undefined,
  ])
  R.map(value => expect(isEmpty(value)).toBe(false), [
    [[]],
    { a: [] },
    'a',
    true,
    false,
    0,
    1,
  ])
})

test('cleanValues', () => {
  R.map(([val, res]) => expect(cleanValues(val)).toEqual(res), [
    [0, '0'],
    [null, 'null'],
    ['  ', ''],
    ['&', '%26'],
    ['   &\n%\t', '%26%20%25'],
  ])
})

test('paramPairs', () => {
  expect(paramPairs('a', 'b')).toEqual('a=b')
  expect(paramPairs('a', [1, 2, 3])).toEqual('a=1,2,3')
})

test('build http fetch init and headers', () => {
  expect(httpOptions()).toEqual({
    method: 'GET',
    credentials: 'same-origin',
    headers: { 'X-CSRFToken': 'NO-CSRF-COOKIE' },
  })
  expect(httpOptions({ method: 'POST' }, 'hello world')).toMatchObject({
    method: 'POST',
    body: 'hello world',
  })
  expect(httpOptions(null, { data: 'hello world' })).toMatchObject({
    method: 'GET',
    body: '{"data":"hello world"}', // json stringified
    headers: { 'Content-Type': 'application/json' }, // correct header
  })
  const form = new FormData()
  form.append('foo', 'bar')
  expect(httpOptions({ method: 'POST' }, form)).toMatchObject({
    method: 'POST',
    body: form,
  })
})

test('search url create', () => {
  expect(searchUrl('stories')({ search: 'hello' })).toBe(
    '/api/stories/?search=hello'
  )
  expect(searchUrl('issues')({ search: '' })).toBe('/api/issues/')
})
