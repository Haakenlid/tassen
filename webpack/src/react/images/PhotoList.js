import 'styles/storylist.scss'
import cx from 'classnames'
import { Clear } from 'components/Icons'
import { connect } from 'react-redux'
import { detailFields } from 'images/model'
import PhotoGrid from 'images/PhotoGrid'
import ListPanel from 'containers/ListPanel'

const MODEL = 'images'

const category = { toggle: true, attr: 'category', model: MODEL }

const filters = [
  { toggle: true, attr: 'limit', model: MODEL, value: 25, label: '25' },
  { toggle: true, attr: 'limit', model: MODEL, value: 75, label: '75' },
  { toggle: true, attr: 'limit', model: MODEL, value: 150, label: '150' },
  { ...category, value: 1, label: 'foto' },
  { ...category, value: 2, label: 'illustrasjon' },
  { ...category, value: 3, label: 'diagram' },
  { ...category, value: 4, label: 'bylinebilde' },
  { ...category, value: 5, label: 'ekstern' },
  { ...category, value: 0, label: 'ukjent' },
]

const PhotoList = ({ model = MODEL }) => {
  return (
    <ListPanel model={MODEL} filters={filters}>
      <PhotoGrid />
    </ListPanel>
  )
}
export default PhotoList
