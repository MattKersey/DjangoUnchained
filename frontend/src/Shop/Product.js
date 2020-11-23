/* eslint react/prop-types: 0 */
import React from 'react'
import { makeStyles, withStyles } from '@material-ui/core/styles'
import clsx from 'clsx'
import Card from '@material-ui/core/Card'
import CardHeader from '@material-ui/core/CardHeader'
import CardMedia from '@material-ui/core/CardMedia'
import CardContent from '@material-ui/core/CardContent'
import CardActions from '@material-ui/core/CardActions'
import Collapse from '@material-ui/core/Collapse'
import IconButton from '@material-ui/core/IconButton'
import Typography from '@material-ui/core/Typography'
import { red } from '@material-ui/core/colors'
import ExpandMoreIcon from '@material-ui/icons/ExpandMore'
import MoreVertIcon from '@material-ui/icons/MoreVert'
import AddShoppingCartIcon from '@material-ui/icons/AddShoppingCart'
const styles = makeStyles((theme) => ({
  root: {
    maxWidth: 345
  },
  media: {
    height: 0,
    paddingTop: '56.25%' // 16:9
  },
  expand: {
    transform: 'rotate(0deg)',
    marginLeft: 'auto',
    transition: theme.transitions.create('transform', {
      duration: theme.transitions.duration.shortest
    })
  },
  expandOpen: {
    transform: 'rotate(180deg)'
  },
  avatar: {
    backgroundColor: red[500]
  },
  bruh: {
    backgroundColor: 'blue'
  }
}))

class Product extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      expanded: false
    }
  }

  handleExpandClick (event) {
    this.setState({ expanded: !this.state.expanded })
  }

  render () {
    const { classes } = this.props
    return (
      <Card className={classes.root}>
        <CardHeader
          action={
            <IconButton aria-label='settings'>
              <MoreVertIcon />
            </IconButton>
        }
          title={this.props.productName}
          subheader='September 14, 2016'
        />
        <CardMedia
          className={classes.media}
          component='img'
          src='https://source.unsplash.com/random'
          title='Paella dish'
          height='140'
        />
        <CardActions style={{ justifyContent: 'space-between' }} disableSpacing>
          <IconButton
            className={clsx(classes.expand, { [classes.expandOpen]: this.state.expanded })}
            onClick={this.handleExpandClick.bind(this)}
            aria-expanded={this.state.expanded}
            aria-label='show more'
          >
            <ExpandMoreIcon />
          </IconButton>
          <Typography paragraph>Quantity: {this.props.stock} </Typography>
          <IconButton onClick={this.props.handleAddToCart} aria-label='share'>
            <AddShoppingCartIcon />
          </IconButton>
        </CardActions>
        <Collapse in={this.state.expanded} timeout='auto' unmountOnExit>
          <CardContent>
            <Typography paragraph>Description: {this.props.description} </Typography>
          </CardContent>
        </Collapse>
      </Card>
    )
  }
}

export default withStyles(styles, { withTheme: true })(Product)
