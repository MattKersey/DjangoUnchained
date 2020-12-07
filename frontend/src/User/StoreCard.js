/* eslint react/prop-types: 0 */
import React from 'react'
import { makeStyles, withStyles } from '@material-ui/core/styles'
import ButtonBase from '@material-ui/core/ButtonBase'
import Card from '@material-ui/core/Card'
import CardContent from '@material-ui/core/CardContent'
import './home.css'
import Typography from '@material-ui/core/Typography'

const styles = makeStyles((theme) => ({
  root: {
    minWidth: 275
  },
  bullet: {
    display: 'inline-block',
    margin: '0 2px',
    transform: 'scale(0.8)'
  },
  title: {
    fontSize: 14
  },
  pos: {
    marginBottom: 12
  }
}))

class StoreCard extends React.Component {
  constructor (props) {
    super(props)
    this.state = { id: this.props.id }
  }

  handleCardClick () {
    window.location = '/shop/' + this.props.id
  }

  render () {
    const { classes } = this.props

    return (
      <div className='root'>
        <Card className='card' style={{ minHeight: '150px' }}>
          <ButtonBase
            className='cardAction'
            onClick={this.handleCardClick.bind(this)}
            width='100%'
            data-testid='card'
          >
            <CardContent width='100%'>
              <Typography variant='h5' component='h2'>
                {this.props.name}
              </Typography>
              <Typography className={classes.title} color='textSecondary' gutterBottom>
                <strong>Address: </strong> {this.props.address}
              </Typography>
              <Typography variang='h6' className={classes.pos} color='textSecondary'>
                <strong>Category: </strong> {this.props.category}
              </Typography>
              <Typography variang='h6' className={classes.pos} color='textSecondary'>
                <strong>Your Role: </strong> {this.props.role}
              </Typography>
            </CardContent>
          </ButtonBase>
        </Card>
      </div>
    )
  }
}

export default withStyles(styles, { withTheme: true })(StoreCard)
