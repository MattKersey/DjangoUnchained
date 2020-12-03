/* global localStorage, fetch, Headers */
/* istanbul ignore file */
/* eslint react/prop-types: 0 */

import React from 'react'
import Typography from '@material-ui/core/Typography'
import { Divider } from '@material-ui/core'

class Success extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      sessionID: '',
      storeName: ''
    }
  }

  componentDidMount () {
    const storeID = this.props.match.params.shopID
    const search = window.location.search
    const params = new URLSearchParams(search)
    const sessionID = params.get('session_id')
    const myHeaders = new Headers()
    myHeaders.append('Authorization', 'Bearer ' + localStorage.getItem('token'))
    myHeaders.append('Content-Type', 'application/json')

    const raw = JSON.stringify({ session_id: sessionID })
    const requestOptions = {
      method: 'POST',
      headers: myHeaders,
      body: raw,
      redirect: 'follow'
    }

    fetch('http://127.0.0.1:8000/api/stores/' + storeID + '/purchase_items/', requestOptions)
      .then(function (response) {
        return response.json()
      })
      .then(function (result) {
        window.location = '/shop/' + storeID + '/'
      })
      .then(function (result) {
        // If `redirectToCheckout` fails due to a browser or network
        // error, you should display the localized error message to your
        // customer using `error.message`.
        if (result.error) {
          console.log(result.error.message)
        }
      })
      .catch(function (error) {
        console.error('Error:', error)
      })
  }

  render () {
    return (
      <div />
    )
  }
}

export default Success
