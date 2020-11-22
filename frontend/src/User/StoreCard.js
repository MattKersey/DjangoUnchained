/* eslint react/prop-types: 0 */
import React from 'react'
import { makeStyles, withStyles } from '@material-ui/core/styles'
import ButtonBase from '@material-ui/core/ButtonBase'
import Card from '@material-ui/core/Card'
import CardContent from '@material-ui/core/CardContent'
import './home.css'
const styles = makeStyles((theme) => ({

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
    return (
      <div className='root'>
        <Card className='card'>
          <ButtonBase
            className='cardAction'
            onClick={this.handleCardClick.bind(this)}
            width='100%'
          >
            <CardContent width='100%'>{this.props.name}</CardContent>
          </ButtonBase>
        </Card>
      </div>
    )
  }
}

export default withStyles(styles, { withTheme: true })(StoreCard)
