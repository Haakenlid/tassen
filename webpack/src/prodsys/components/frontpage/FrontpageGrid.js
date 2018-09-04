import cx from 'classnames'
import { connect } from 'react-redux'
import ModelField from 'components/ModelField'
import { MODEL, actions, selectors, fields } from './model.js'
import { FeedItem } from 'components/NewsFeed/FeedItem.js'
import Debug from 'components/Debug'
import './FrontpageGrid.scss'

const FeedItemWrapper = ({ onClick, className, children }) => (
  <div className={className} onClick={onClick} children={children} />
)

const ConnectedFeedItem = connect(
  (state, { pk }) => {
    const data = selectors.getItem(pk)(state) || {}
    const selected = selectors.getCurrentItemId(state) === pk
    const { dirty, published } = data
    const className = cx('FeedItemWrapper', {
      dirty,
      selected,
      unpublished: !published,
    })
    return { sectionName: data.story.section, ...data, className, model: MODEL }
  },
  (dispatch, { pk }) => ({
    onClick: e => dispatch(actions.reverseUrl({ id: pk })),
  }),
)(props => <FeedItem Wrapper={FeedItemWrapper} {...props} />)

const FrontpageGrid = ({ items = [] }) => (
  <section
    className="NewsFeed"
    style={{
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '1rem',
    }}
  >
    {R.pipe(R.map(pk => <ConnectedFeedItem key={pk} pk={pk} />))(items)}
  </section>
)

const mapStateToProps = (state, ownProps) => {
  const ids = selectors.getItemList(state)
  const items = selectors.getItems(state)
  const sorted = R.pipe(
    R.pick(ids),
    R.map(props => ({
      ...props,
      sortKey: props.baserank + parseFloat(props.priority),
    })),
    R.values,
    R.sortWith([R.descend(R.prop('sortKey'))]),
    R.pluck('id'),
  )

  return { items: sorted(items) }
}

export default connect(mapStateToProps)(FrontpageGrid)
