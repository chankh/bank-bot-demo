import { Component } from '@angular/core'

export class Transaction {
  date: string;
  description: string;
  refId: string;
  amount: number;
  currency: string;
  type: string;
  runningBalance: number;
}

const TRANSACTIONS: Transaction[] = [
{"date":"2016-04-29","description":"INTEREST EARNED","refId":"001327-00026","amount":184.87,"currency":"HKD","type":"DEBIT","runningBalance":13641.11},{"date":"2016-03-31","description":"INTEREST EARNED","refId":"10000007027121000012740","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":13640.55},{"date":"2016-02-29","description":"INTEREST EARNED","refId":"10000007027121000012750","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":13639.97},{"date":"2016-01-29","description":"INTEREST EARNED","refId":"75454917088008183951892","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":13639.43},{"date":"2015-12-31","description":"INTEREST EARNED","refId":"75454917076008183951896","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":13638.85},{"date":"2015-12-07","description":"LOAN INTEREST PAYMENT","refId":"60401123234943307076001","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":13638.26},{"date":"2015-11-30","description":"INTEREST EARNED","refId":"60314095102745135076001","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":14428.88},{"date":"2015-11-25","description":"LOAN INTEREST PAYMENT","refId":"19999999987088000010450","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":14428.27},{"date":"2015-10-31","description":"INTEREST EARNED","refId":"BIMI51605310001483","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":15021.24},{"date":"2015-09-30","description":"INTEREST EARNED","refId":"BIMI51606280001604","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":15020.6},{"date":"2016-04-29","description":"INTEREST EARNED","refId":"3001327-00026","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":13641.11},{"date":"2016-03-31","description":"INTEREST EARNED","refId":"310000007027121000012740","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":13640.55},{"date":"2016-02-29","description":"INTEREST EARNED","refId":"310000007027121000012750","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":13639.97},{"date":"2016-01-29","description":"INTEREST EARNED","refId":"375454917088008183951892","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":13639.43},{"date":"2015-12-31","description":"INTEREST EARNED","refId":"375454917076008183951896","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":13638.85},{"date":"2015-12-07","description":"LOAN INTEREST PAYMENT","refId":"360401123234943307076001","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":13638.26},{"date":"2015-11-30","description":"INTEREST EARNED","refId":"360314095102745135076001","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":14428.88},{"date":"2015-11-25","description":"LOAN INTEREST PAYMENT","refId":"319999999987088000010450","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":14428.27},{"date":"2015-10-31","description":"INTEREST EARNED","refId":"3BIMI51605310001483","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":15021.24},{"date":"2015-09-30","description":"INTEREST EARNED","refId":"3BIMI51606280001604","amount":133,"currency":"HKD","type":"DEBIT","runningBalance":15020.6}
]

@Component({
  selector: 'account-transactions',
  template: `
<div class="panel panel-info">
  <!-- Default panel contents -->
  <div class="panel-heading">Transactions</div>
  <!-- Table -->
  <div class="table-responsive">
  <table class="table table-hover">
    <tr>
      <th>Date</th>
      <th>Description</th>
      <th>Reference No.</th>
      <th>Amount</th>
      <th>Balance</th>
    </tr>
    <tr *ngFor="let t of transactions">
      <td>{{t.date}}</td>
      <td>{{t.description}}</td>
      <td>{{t.refId}}</td>
      <td>{{t.amount | currency:t.currency:true:'1.2-2'}} {{t.type == 'DEBIT' ? 'DR' : 'CR'}}</td>
      <td>{{t.runningBalance | currency:t.currency:true:'1.2-2'}}</td>
    </tr>
  </table>
  </div>
</div>
  `
})

export class AccountTransactionsComponent {
    transactions = TRANSACTIONS;
}



