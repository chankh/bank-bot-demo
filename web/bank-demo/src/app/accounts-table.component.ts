import { Component } from '@angular/core'

export class Account {
  id: string;
  number: string;
  name: string;
  currency: string;
  currentBal: number;
  availableBal: number;
}

const ACCOUNTS: Account[] = [
  { id: "355a515030616a53576b6a65797359506a634175764a734a3238314e4668627349486a676f7449463949453d", number: "XXXXXX1847", name: "Personal Savings Account", currency: "HKD", currentBal: 13642.83, availableBal: 13642.83},
  { id: "57706472614c786a31716f5855743050597473703259494179505959776a377370614b364167516a57336b3d", number: "XXXXXX1369", name: "HKD CASH TRADING ACCOUNT", currency: "HKD", currentBal: 4467.15, availableBal: 4467.15},
  { id: "41375159436b366b32335a6b566d53315753684d2b69464f43427347654b496e2f6a4f6d4971546e622f773d", number: "XXXXXX5840", name: "CASH PLUS", currency: "HKD", currentBal: 11562.5, availableBal: 11562.5},
  { id: "755a774e674f2f6d4b3074355a5439506d35464c67455251396e56794851304443306376467a45545242733d", number: "XXXXXX0308", name: "UNFIXED TD", currency: "HKD", currentBal: 9.04, availableBal: 9.04},
  { id: "336748697936664d4f72445456356763447756546362562b527953457866685839685969766c32374d79733d", number: "XXXXXX5802", name: "PREMIUM ACCOUNT", currency: "HKD", currentBal: 26589.01, availableBal: 26589.01},
  { id: "416b79676b52556f53465a61722b4a68647a6f677273346443794a503441444669316e3163452b767976343d", number: "XXXXXX2302", name: "NRI MUTUAL FUNDS RDR ACCOUNT", currency: "HKD", currentBal: 665644.98, availableBal: 665644.98},
  { id: "6d7a6272592b334b736b46417365786d31543653454a3044496a3447584941333679792b4f3436325546513d", number: "XXXXXX7001", name: "SECURITIES BROKERAGE CASH ACCO", currency: "HKD", currentBal: 93561.68, availableBal: 93561.68},
]

@Component({
  selector: 'accounts-table',
  template: `
  <div class="row">
    <div class="col-xs-6 col-md-4">
      <div class="panel panel-primary">
        <!-- Default panel contents -->
        <div class="panel-heading">Savings and Investments</div>
        <!-- Accounts -->
        <div class="list-group" *ngFor="let a of accounts; let i = index">
            <a href="#" class="list-group-item {{i==0 ? 'active' : ''}}">
            <h5 class="list-group-item-heading">{{a.name}} ({{a.number}})</h5>
            <p class="list-gropu-item-text">{{a.currentBal | currency:a.currency:true:'1.2-2'}}</p>
          </a>
        </div>
      </div>
    </div>
    <div class="col-xs-12 col-md-8">
      <account-transactions></account-transactions>
    </div>
  </div>
  `
})
export class AccountsTableComponent {
  accounts = ACCOUNTS;
}
