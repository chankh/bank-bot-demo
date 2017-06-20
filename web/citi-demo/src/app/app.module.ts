import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { AccountsTableComponent } from './accounts-table.component';
import { AccountTransactionsComponent } from './account-transactions.component';

@NgModule({
  declarations: [
    AppComponent,
    AccountsTableComponent,
    AccountTransactionsComponent
  ],
  imports: [
    BrowserModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
