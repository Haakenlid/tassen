import { all, fork, call, put, take } from 'redux-saga/effects'
import authSaga from 'sagas/auth'
import errorSaga from 'sagas/error'
import apiSaga from 'sagas/apisaga'
import { modelActions } from 'ducks/basemodel'
import { requestUser } from 'ducks/auth'
import { push, LOCATION_CHANGED } from 'redux-little-router'

function* rootSaga() {
  yield [fork(apiSaga), fork(errorSaga), fork(authSaga), call(initialData)]
}

function* initialData() {
  yield put(modelActions('storytypes').itemsRequested())
  yield put(modelActions('stories').itemsRequested())
  yield put(modelActions('images').itemsRequested())
  yield put(modelActions('contributors').itemsRequested())
  yield put(modelActions('issues').itemsRequested())
  yield put(requestUser())
  const action = yield take(LOCATION_CHANGED)
  if (R.pathEq(['payload', 'route'], '/')(action)) {
    yield put(push('/stories'))
  }
}

export default rootSaga
