
import axios from 'axios'

/**
 *
 * @param {*} accesstoken This is the accesstoken of the user obtained from Google
 */
const googleLogin = async (accesstoken) => {
  const res = await axios.post(
    'http://127.0.0.1:8000/rest-auth/google/',
    {
      access_token: accesstoken
    }
  )
  return await res
}

export default googleLogin
