import { connect } from 'react-redux'
import cx from 'classnames'
import { timeoutDebounce, inViewPort } from 'utils/misc'
import { getItems, getFeed, feedRequested } from 'ducks/newsFeed'
import { getStory, storiesRequested } from 'ducks/publicstory'
import LoadMore from 'components/LoadMore'
import FeedItem from './FeedItem'

const mapItemStateToProps = (state, { story, addRef }) => {
  const fullStory = getStory(story.id)(state)
  if (!fullStory) return { _ref: addRef, fetchStatus: 'unfetched' }
  addRef(null)
  return { fetchStatus: fullStory.fetching ? 'fetching' : 'fetched' }
}
const ConnectedFeedItem = connect(mapItemStateToProps)(FeedItem)

class NewsFeed extends React.Component {
  constructor(props) {
    super(props)
    this.itemRefs = {}
    this.addRef = id => el => (this.itemRefs[id] = el)
    this.addHandler = () => {
      this.scrollHandler = timeoutDebounce(ev => this.feedScrolled(), 500)
    }
    this.addHandler()
  }

  feedScrolled() {
    const itemsVisible = R.pipe(
      R.without(R.isNil),
      R.filter(inViewPort),
      R.keys,
    )(this.itemRefs)
    if (R.isEmpty(itemsVisible)) return
    if (this.props.storiesRequested) this.props.storiesRequested(itemsVisible)
  }

  componentDidMount() {
    if (module.hot) this.addHandler()
    window.addEventListener('scroll', this.scrollHandler, {
      capture: true,
      passive: true,
    })
    this.scrollHandler()
  }
  componentWillUnmount() {
    window.removeEventListener('scroll', this.scrollHandler)
  }
  componentDidUpdate() {
    if (module.hot) this.addHandler()
    this.scrollHandler()
  }

  render() {
    const { items, fetching, next, feedRequested, className } = this.props
    const offset = items.length ? R.last(items).order : null
    const fetchMore = () => feedRequested({ offset })
    return (
      <article className={cx('NewsFeed', className)}>
        {items.map(props => (
          <ConnectedFeedItem
            addRef={this.addRef(props.story.id)}
            key={props.id}
            {...props}
          />
        ))}
        <LoadMore fetchMore={fetchMore} fetching={fetching} next={next} />
      </article>
    )
  }
}

export { NewsFeed }

export default connect(s => ({ items: getItems(s), ...getFeed(s) }), {
  feedRequested,
  storiesRequested,
})(NewsFeed)
