# app/models/fund_raising.py

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

class FundRaising:
    def __init__(self, allocation_data, vesting_data, airdrop_module, initial_total_supply, public_sale_valuation):
        self.allocation_data = pd.DataFrame(allocation_data)
        self.vesting_data = pd.DataFrame(vesting_data)
        self.airdrop_module = airdrop_module
        self.initial_total_supply = initial_total_supply
        self.public_sale_valuation = public_sale_valuation

    def generate_pie_chart(self):
        self.allocation_data['tokens'] = self.allocation_data['percentage'] * self.initial_total_supply / 100
        fig = go.Figure(data=[go.Pie(
            labels=self.allocation_data['allocation'],
            values=self.allocation_data['tokens'],
            textinfo='label+value',
            insidetextorientation='radial',
            hovertemplate='%{label}<br>Tokens: %{value:,.0f}<br>Percentage: %{percent}'
        )])
        
        fig.update_layout(
            title_text=f'Token Allocation (Total Supply: {self.initial_total_supply:,})',
            showlegend=True
        )
        
        return fig

    def generate_vesting_chart(self):
        start_date = self.vesting_data['vestingStart'].min()
        end_date = (pd.to_datetime(start_date) + pd.Timedelta(days=365*4)).strftime('%Y-%m-%d')
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        vesting_data = pd.DataFrame(index=date_range)
        
        for _, row in self.vesting_data.iterrows():
            vesting_start = pd.to_datetime(row['vestingStart'])
            cliff = pd.Timedelta(days=30 * row['cliff'])
            vesting_period = pd.Timedelta(days=30 * row['vestingPeriod'])
            vesting_end = vesting_start + cliff + vesting_period
            
            if row['tgeUnlock'] > 0:
                vesting_data.loc[vesting_start, row['allocation']] = row['tokens'] * row['tgeUnlock'] / 100
            
            vesting_days = (vesting_end - (vesting_start + cliff)).days
            daily_vesting = (row['tokens'] * (100 - row['tgeUnlock']) / 100) / vesting_days if vesting_days > 0 else 0
            
            for day in range((cliff + pd.Timedelta(days=1)).days, (vesting_period + cliff).days + 1):
                current_date = vesting_start + pd.Timedelta(days=day)
                if current_date <= vesting_end:
                    vesting_data.loc[current_date, row['allocation']] = daily_vesting
        
        # add airdrop #2 data
        airdrop_dates = [self.airdrop_module['date1'], self.airdrop_module['date2'], self.airdrop_module['date3']]
        airdrop_amounts = [self.airdrop_module['amount1'], self.airdrop_module['amount2'], self.airdrop_module['amount3']]
        for date, amount in zip(airdrop_dates, airdrop_amounts):
            if pd.notna(date) and amount > 0:
                vesting_data.loc[date, 'Airdrop #2'] = self.airdrop_module['tokens'] * amount / 100
        
        vesting_data = vesting_data.fillna(0).cumsum()
        
        # cap vesting data at initial total supply
        vesting_data = vesting_data.clip(upper=self.initial_total_supply)
        
        fig = go.Figure()
        for column in vesting_data.columns:
            fig.add_trace(go.Scatter(
                x=vesting_data.index, 
                y=vesting_data[column],
                mode='lines',
                name=column,
                stackgroup='one'
            ))
        
        # add line for total supply
        fig.add_trace(go.Scatter(
            x=[vesting_data.index[0], vesting_data.index[-1]],
            y=[self.initial_total_supply, self.initial_total_supply],
            mode='lines',
            name='Total Supply',
            line=dict(color='red', dash='dash')
        ))
        
        public_sale_tokens = self.vesting_data.loc[self.vesting_data['allocation'] == 'Public Sale', 'tokens'].values[0]
        token_price = self.public_sale_valuation / public_sale_tokens
        implied_market_cap = token_price * self.initial_total_supply
        
        fig.update_layout(
            title_text=f'Token Vesting Schedule<br>Implied Market Cap: ${implied_market_cap:,.2f}<br>Token Price: ${token_price:.4f}',
            xaxis_title='Date',
            yaxis_title='Vested Tokens',
            legend_title='Allocation',
            hovermode='x unified'
        )
        
        return fig

    def generate_charts(self):
        return {
            'pie_chart': self.generate_pie_chart().to_json(),
            'vesting_chart': self.generate_vesting_chart().to_json()
        }