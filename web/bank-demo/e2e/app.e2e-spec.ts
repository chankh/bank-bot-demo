import { CitiDemoPage } from './app.po';

describe('citi-demo App', () => {
  let page: CitiDemoPage;

  beforeEach(() => {
    page = new CitiDemoPage();
  });

  it('should display welcome message', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('Welcome to app!!');
  });
});
