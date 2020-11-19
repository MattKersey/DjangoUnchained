import React, { Component } from 'react'
import GoogleLogin from 'react-google-login'

class GoogleSocialAuth extends Component {
  render () {
    const googleResponse = (response) => {
      console.log(response)
      debugger
    }
    return (
      <div mt='10' className='App'>
        <GoogleLogin
          clientId='1099310677669-4lsl049eq46fe9tpct8ro6em04rcm0n1.apps.googleusercontent.com'
          buttonText='LOGIN WITH GOOGLE'
          onSuccess={googleResponse}
          onFailure={googleResponse}
        />
      </div>
    )
  }
}

export default GoogleSocialAuth
