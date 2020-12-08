/* istanbul ignore file */
/* eslint react/prop-types: 0 */

import React from 'react'
import { XYPlot, VerticalBarSeries, XAxis, YAxis, LabelSeries } from 'react-vis'
import Box from '@material-ui/core/Box'
import Typography from '@material-ui/core/Typography'
class Chart extends React.Component {
  render () {
    const data = this.props.data
    const chartWidth = 500
    const chartHeight = 400
    const chartDomain = [0, chartHeight]
    return (
      <Box display='flex' mb={3}>
        <Box borderRight={1} pr={1} mr={2}>
          <XYPlot
            width={chartWidth}
            height={chartHeight}
            yDomain={chartDomain}
            xType='time'
          >
            <XAxis title='Time' />
            <YAxis title='Purchase' />
            <VerticalBarSeries data={data} />
            <LabelSeries
              data={data.map(obj => {
                return { ...obj, label: '$' + obj.y.toString() }
              })}
              labelAnchorX='middle'
              labelAnchorY='text-after-edge'
            />
          </XYPlot>
        </Box>
        <Box>
          <Typography component='h1' variant='h5'>
            Total Revenue
          </Typography>
          {this.props.revenue}
          <Typography component='h1' variant='h5'>
            Best Selling:
          </Typography>
          {this.props.bestSelling} ({this.props.bestSellingPurchaseCount} Purchased)
        </Box>
      </Box>
    )
  }
}

export default Chart
