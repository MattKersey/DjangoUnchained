/* global localStorage */
import React from 'react'
import axios from 'axios'
import { withStyles } from '@material-ui/core/styles'
import PropTypes from 'prop-types'

const styles = theme => ({})

class LoginRedirect extends React.Component {
  componentDidMount () {
    const { location: { search } } = this.props
    console.log(search)
    axios.get('http://127.0.0.1:8000/authredirect/' + search)
      .then((response) => {
        const newToken = response.data.access_token
        localStorage.setItem('token', newToken)
        window.location = '/'
      })
  }

  render () {
    return null
  }
}

LoginRedirect.propTypes = {
  classes: PropTypes.any,
  location: PropTypes.shape({
    search: PropTypes.any
  })
}

export default withStyles(styles, { withTheme: true })(LoginRedirect)
